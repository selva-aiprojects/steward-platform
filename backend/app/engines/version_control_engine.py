"""
Version Control Engine for Futures, Options, and Currencies Strategies

This module implements the Version Control Engine responsible for:
1. Managing strategy versions and revisions
2. Tracking changes to trading strategies
3. Strategy deployment and rollback capabilities
4. A/B testing of strategy versions
5. Compliance and audit trail management
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid
import json
import hashlib

logger = logging.getLogger(__name__)


class VersionControlEngineInterface(ABC):
    """Abstract interface for Version Control Engine"""

    @abstractmethod
    async def create_strategy_version(self, strategy_id: str, strategy_config: Dict[str, Any], version_notes: str) -> Dict[str, Any]:
        """Create a new version of a strategy"""
        pass

    @abstractmethod
    async def deploy_strategy_version(self, strategy_id: str, version_id: str) -> Dict[str, Any]:
        """Deploy a specific version of a strategy"""
        pass

    @abstractmethod
    async def rollback_strategy_version(self, strategy_id: str, version_id: str) -> Dict[str, Any]:
        """Rollback to a previous version of a strategy"""
        pass

    @abstractmethod
    async def compare_strategy_versions(self, strategy_id: str, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """Compare two versions of a strategy"""
        pass

    @abstractmethod
    async def get_strategy_history(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get history of strategy versions"""
        pass

    @abstractmethod
    async def run_ab_test(self, strategy_id: str, version_a: str, version_b: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run A/B test between two strategy versions"""
        pass


class VersionControlEngine(VersionControlEngineInterface):
    """
    Main Version Control Engine implementation for Futures, Options, and Currencies
    """

    def __init__(self):
        self.strategy_versions = {}
        self.deployments = {}
        self.audit_trail = []
        logger.info("Version Control Engine initialized")

    async def create_strategy_version(self, strategy_id: str, strategy_config: Dict[str, Any], version_notes: str) -> Dict[str, Any]:
        """Create a new version of a strategy"""
        try:
            # Generate unique version ID
            version_id = str(uuid.uuid4())
            
            # Create version hash for integrity check
            config_hash = hashlib.sha256(json.dumps(strategy_config, sort_keys=True).encode()).hexdigest()
            
            # Create version record
            version_record = {
                "version_id": version_id,
                "strategy_id": strategy_id,
                "config": strategy_config,
                "version_notes": version_notes,
                "created_at": datetime.now().isoformat(),
                "created_by": strategy_config.get("created_by", "system"),
                "config_hash": config_hash,
                "status": "DRAFT",  # DRAFT, REVIEW, APPROVED, DEPLOYED, ARCHIVED
                "deployment_count": 0
            }
            
            # Initialize strategy version history if not exists
            if strategy_id not in self.strategy_versions:
                self.strategy_versions[strategy_id] = []
            
            # Add version to history
            self.strategy_versions[strategy_id].append(version_record)
            
            # Add to audit trail
            audit_entry = {
                "event_type": "STRATEGY_VERSION_CREATED",
                "strategy_id": strategy_id,
                "version_id": version_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": strategy_config.get("created_by", "system"),
                "details": {
                    "version_notes": version_notes,
                    "config_hash": config_hash
                }
            }
            self.audit_trail.append(audit_entry)
            
            logger.info(f"Created version {version_id} for strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "version_id": version_id,
                "message": f"Version {version_id} created for strategy {strategy_id}"
            }
        except Exception as e:
            logger.error(f"Error creating strategy version: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def deploy_strategy_version(self, strategy_id: str, version_id: str) -> Dict[str, Any]:
        """Deploy a specific version of a strategy"""
        try:
            # Find the version to deploy
            version_record = await self._find_version(strategy_id, version_id)
            if not version_record:
                return {
                    "success": False,
                    "error": f"Version {version_id} not found for strategy {strategy_id}"
                }
            
            # Check if version is approved for deployment
            if version_record["status"] not in ["APPROVED", "DEPLOYED"]:
                return {
                    "success": False,
                    "error": f"Version {version_id} is not approved for deployment (status: {version_record['status']})"
                }
            
            # Deploy the strategy version
            deployment_id = str(uuid.uuid4())
            
            deployment_record = {
                "deployment_id": deployment_id,
                "strategy_id": strategy_id,
                "version_id": version_id,
                "deployed_at": datetime.now().isoformat(),
                "deployed_by": version_record.get("created_by", "system"),
                "status": "ACTIVE",  # ACTIVE, INACTIVE, FAILED
                "environment": "production",  # production, staging, development
                "activation_params": version_record["config"].get("activation_params", {})
            }
            
            # Store deployment
            if strategy_id not in self.deployments:
                self.deployments[strategy_id] = []
            self.deployments[strategy_id].append(deployment_record)
            
            # Update version status
            version_record["status"] = "DEPLOYED"
            version_record["deployment_count"] += 1
            
            # Add to audit trail
            audit_entry = {
                "event_type": "STRATEGY_VERSION_DEPLOYED",
                "strategy_id": strategy_id,
                "version_id": version_id,
                "deployment_id": deployment_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": version_record.get("created_by", "system"),
                "details": {
                    "environment": deployment_record["environment"]
                }
            }
            self.audit_trail.append(audit_entry)
            
            logger.info(f"Deployed version {version_id} for strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "version_id": version_id,
                "deployment_id": deployment_id,
                "message": f"Version {version_id} deployed for strategy {strategy_id}"
            }
        except Exception as e:
            logger.error(f"Error deploying strategy version: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def rollback_strategy_version(self, strategy_id: str, version_id: str) -> Dict[str, Any]:
        """Rollback to a previous version of a strategy"""
        try:
            # Find the version to rollback to
            version_record = await self._find_version(strategy_id, version_id)
            if not version_record:
                return {
                    "success": False,
                    "error": f"Version {version_id} not found for strategy {strategy_id}"
                }
            
            # Find current active deployment
            current_deployment = await self._get_active_deployment(strategy_id)
            if not current_deployment:
                return {
                    "success": False,
                    "error": f"No active deployment found for strategy {strategy_id}"
                }
            
            # Check if we're rolling back to a different version
            if current_deployment["version_id"] == version_id:
                return {
                    "success": False,
                    "error": f"Version {version_id} is already active for strategy {strategy_id}"
                }
            
            # Create rollback deployment
            rollback_id = str(uuid.uuid4())
            
            rollback_record = {
                "rollback_id": rollback_id,
                "strategy_id": strategy_id,
                "from_version": current_deployment["version_id"],
                "to_version": version_id,
                "rolled_back_at": datetime.now().isoformat(),
                "rolled_back_by": current_deployment.get("deployed_by", "system"),
                "status": "COMPLETED",  # COMPLETED, FAILED
                "reason": "Manual rollback",
                "environment": current_deployment["environment"]
            }
            
            # Deploy the target version
            deployment_result = await self.deploy_strategy_version(strategy_id, version_id)
            if not deployment_result["success"]:
                return deployment_result
            
            # Update current deployment status
            current_deployment["status"] = "ROLLED_BACK"
            
            # Add to audit trail
            audit_entry = {
                "event_type": "STRATEGY_VERSION_ROLLBACK",
                "strategy_id": strategy_id,
                "from_version": current_deployment["version_id"],
                "to_version": version_id,
                "rollback_id": rollback_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": current_deployment.get("deployed_by", "system"),
                "details": {
                    "reason": "Manual rollback"
                }
            }
            self.audit_trail.append(audit_entry)
            
            logger.info(f"Rolled back strategy {strategy_id} from {current_deployment['version_id']} to {version_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "from_version": current_deployment["version_id"],
                "to_version": version_id,
                "rollback_id": rollback_id,
                "message": f"Rolled back strategy {strategy_id} to version {version_id}"
            }
        except Exception as e:
            logger.error(f"Error rolling back strategy version: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def compare_strategy_versions(self, strategy_id: str, version1_id: str, version2_id: str) -> Dict[str, Any]:
        """Compare two versions of a strategy"""
        try:
            # Find both versions
            version1 = await self._find_version(strategy_id, version1_id)
            version2 = await self._find_version(strategy_id, version2_id)
            
            if not version1:
                return {
                    "success": False,
                    "error": f"Version {version1_id} not found for strategy {strategy_id}"
                }
            
            if not version2:
                return {
                    "success": False,
                    "error": f"Version {version2_id} not found for strategy {strategy_id}"
                }
            
            # Compare configurations
            comparison = await self._compare_configs(version1["config"], version2["config"])
            
            comparison_result = {
                "strategy_id": strategy_id,
                "version1_id": version1_id,
                "version2_id": version2_id,
                "comparison": comparison,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Compared versions {version1_id} and {version2_id} for strategy {strategy_id}")
            
            return {
                "success": True,
                "comparison_result": comparison_result
            }
        except Exception as e:
            logger.error(f"Error comparing strategy versions: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_strategy_history(self, strategy_id: str) -> List[Dict[str, Any]]:
        """Get history of strategy versions"""
        try:
            if strategy_id not in self.strategy_versions:
                return {
                    "success": False,
                    "error": f"No versions found for strategy {strategy_id}"
                }
            
            history = self.strategy_versions[strategy_id]
            
            # Sort by creation date (newest first)
            sorted_history = sorted(history, key=lambda x: x["created_at"], reverse=True)
            
            strategy_history = {
                "strategy_id": strategy_id,
                "versions": sorted_history,
                "total_versions": len(sorted_history),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Retrieved history for strategy {strategy_id} ({len(sorted_history)} versions)")
            
            return {
                "success": True,
                "strategy_history": strategy_history
            }
        except Exception as e:
            logger.error(f"Error retrieving strategy history: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def run_ab_test(self, strategy_id: str, version_a: str, version_b: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run A/B test between two strategy versions"""
        try:
            # Validate that both versions exist
            version_a_record = await self._find_version(strategy_id, version_a)
            version_b_record = await self._find_version(strategy_id, version_b)
            
            if not version_a_record:
                return {
                    "success": False,
                    "error": f"Version {version_a} not found for strategy {strategy_id}"
                }
            
            if not version_b_record:
                return {
                    "success": False,
                    "error": f"Version {version_b} not found for strategy {strategy_id}"
                }
            
            # Validate that both versions are approved
            if version_a_record["status"] not in ["APPROVED", "DEPLOYED"]:
                return {
                    "success": False,
                    "error": f"Version {version_a} is not approved for testing"
                }
            
            if version_b_record["status"] not in ["APPROVED", "DEPLOYED"]:
                return {
                    "success": False,
                    "error": f"Version {version_b} is not approved for testing"
                }
            
            # Generate unique test ID
            test_id = str(uuid.uuid4())
            
            # Create A/B test record
            ab_test = {
                "test_id": test_id,
                "strategy_id": strategy_id,
                "version_a": version_a,
                "version_b": version_b,
                "config": test_config,
                "start_time": datetime.now().isoformat(),
                "end_time": None,
                "status": "RUNNING",
                "allocation": test_config.get("allocation", {"version_a": 0.5, "version_b": 0.5}),  # Default 50/50 split
                "metrics": {
                    "version_a": {"trades": 0, "pnl": 0, "win_rate": 0, "sharpe_ratio": 0},
                    "version_b": {"trades": 0, "pnl": 0, "win_rate": 0, "sharpe_ratio": 0}
                },
                "winner": None,
                "confidence_level": 0
            }
            
            # For now, just store the test configuration
            # In a real implementation, this would start the A/B test execution
            # and continuously update metrics
            
            # Add to audit trail
            audit_entry = {
                "event_type": "AB_TEST_STARTED",
                "strategy_id": strategy_id,
                "test_id": test_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": test_config.get("initiated_by", "system"),
                "details": {
                    "version_a": version_a,
                    "version_b": version_b,
                    "allocation": ab_test["allocation"]
                }
            }
            self.audit_trail.append(audit_entry)
            
            logger.info(f"Started A/B test {test_id} for strategy {strategy_id} (versions {version_a} vs {version_b})")
            
            return {
                "success": True,
                "test_id": test_id,
                "message": f"A/B test started for strategy {strategy_id}",
                "test_details": {
                    "strategy_id": strategy_id,
                    "version_a": version_a,
                    "version_b": version_b,
                    "allocation": ab_test["allocation"],
                    "start_time": ab_test["start_time"]
                }
            }
        except Exception as e:
            logger.error(f"Error running A/B test: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def promote_version(self, strategy_id: str, version_id: str, promotion_notes: str) -> Dict[str, Any]:
        """Promote a version from DRAFT to APPROVED"""
        try:
            version_record = await self._find_version(strategy_id, version_id)
            if not version_record:
                return {
                    "success": False,
                    "error": f"Version {version_id} not found for strategy {strategy_id}"
                }
            
            if version_record["status"] != "DRAFT":
                return {
                    "success": False,
                    "error": f"Version {version_id} is not in DRAFT status (current: {version_record['status']})"
                }
            
            # Update version status
            version_record["status"] = "APPROVED"
            version_record["promotion_notes"] = promotion_notes
            version_record["promoted_at"] = datetime.now().isoformat()
            version_record["promoted_by"] = version_record.get("created_by", "system")
            
            # Add to audit trail
            audit_entry = {
                "event_type": "STRATEGY_VERSION_PROMOTED",
                "strategy_id": strategy_id,
                "version_id": version_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": version_record.get("created_by", "system"),
                "details": {
                    "promotion_notes": promotion_notes
                }
            }
            self.audit_trail.append(audit_entry)
            
            logger.info(f"Promoted version {version_id} for strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "version_id": version_id,
                "message": f"Version {version_id} promoted for strategy {strategy_id}"
            }
        except Exception as e:
            logger.error(f"Error promoting strategy version: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def archive_version(self, strategy_id: str, version_id: str, reason: str) -> Dict[str, Any]:
        """Archive a strategy version"""
        try:
            version_record = await self._find_version(strategy_id, version_id)
            if not version_record:
                return {
                    "success": False,
                    "error": f"Version {version_id} not found for strategy {strategy_id}"
                }
            
            if version_record["status"] == "ARCHIVED":
                return {
                    "success": False,
                    "error": f"Version {version_id} is already archived"
                }
            
            # Check if version is currently deployed
            active_deployment = await self._get_active_deployment(strategy_id)
            if active_deployment and active_deployment["version_id"] == version_id:
                return {
                    "success": False,
                    "error": f"Cannot archive version {version_id} as it is currently deployed"
                }
            
            # Archive the version
            version_record["status"] = "ARCHIVED"
            version_record["archived_at"] = datetime.now().isoformat()
            version_record["archived_reason"] = reason
            version_record["archived_by"] = version_record.get("created_by", "system")
            
            # Add to audit trail
            audit_entry = {
                "event_type": "STRATEGY_VERSION_ARCHIVED",
                "strategy_id": strategy_id,
                "version_id": version_id,
                "timestamp": datetime.now().isoformat(),
                "user_id": version_record.get("created_by", "system"),
                "details": {
                    "reason": reason
                }
            }
            self.audit_trail.append(audit_entry)
            
            logger.info(f"Archived version {version_id} for strategy {strategy_id}")
            
            return {
                "success": True,
                "strategy_id": strategy_id,
                "version_id": version_id,
                "message": f"Version {version_id} archived for strategy {strategy_id}"
            }
        except Exception as e:
            logger.error(f"Error archiving strategy version: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_audit_trail(self, strategy_id: Optional[str] = None, event_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail for compliance and monitoring"""
        try:
            filtered_audit = self.audit_trail
            
            if strategy_id:
                filtered_audit = [entry for entry in filtered_audit if entry.get("strategy_id") == strategy_id]
            
            if event_type:
                filtered_audit = [entry for entry in filtered_audit if entry.get("event_type") == event_type]
            
            # Sort by timestamp (most recent first)
            sorted_audit = sorted(filtered_audit, key=lambda x: x["timestamp"], reverse=True)[:limit]
            
            logger.info(f"Retrieved audit trail for strategy {strategy_id or 'all'} ({len(sorted_audit)} events)")
            
            return {
                "success": True,
                "audit_trail": sorted_audit
            }
        except Exception as e:
            logger.error(f"Error retrieving audit trail: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _find_version(self, strategy_id: str, version_id: str) -> Optional[Dict[str, Any]]:
        """Find a specific version of a strategy"""
        if strategy_id not in self.strategy_versions:
            return None
        
        for version in self.strategy_versions[strategy_id]:
            if version["version_id"] == version_id:
                return version
        
        return None

    async def _get_active_deployment(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """Get the currently active deployment for a strategy"""
        if strategy_id not in self.deployments:
            return None
        
        for deployment in reversed(self.deployments[strategy_id]):  # Check most recent first
            if deployment["status"] == "ACTIVE":
                return deployment
        
        return None

    async def _compare_configs(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two strategy configurations"""
        # This would implement a detailed comparison of strategy configurations
        # For now, returning a simple comparison
        
        # Convert configs to JSON strings for comparison
        config1_str = json.dumps(config1, sort_keys=True)
        config2_str = json.dumps(config2, sort_keys=True)
        
        # Find differences
        differences = []
        
        # Compare top-level keys
        keys1 = set(config1.keys())
        keys2 = set(config2.keys())
        
        added_keys = keys2 - keys1
        removed_keys = keys1 - keys2
        common_keys = keys1 & keys2
        
        if added_keys:
            differences.append({
                "type": "added",
                "keys": list(added_keys),
                "values": {k: config2[k] for k in added_keys}
            })
        
        if removed_keys:
            differences.append({
                "type": "removed",
                "keys": list(removed_keys),
                "values": {k: config1[k] for k in removed_keys}
            })
        
        # Compare values for common keys
        changed_values = {}
        for key in common_keys:
            if config1[key] != config2[key]:
                changed_values[key] = {
                    "old_value": config1[key],
                    "new_value": config2[key]
                }
        
        if changed_values:
            differences.append({
                "type": "changed",
                "values": changed_values
            })
        
        comparison_result = {
            "configs_equal": config1_str == config2_str,
            "differences": differences,
            "similarity_score": 0.0  # Would be calculated based on similarity
        }
        
        return comparison_result

    async def _validate_strategy_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate strategy configuration"""
        errors = []
        
        # Check required fields
        required_fields = ["asset_class", "strategy_type", "symbol"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # Validate asset class
        if "asset_class" in config:
            valid_asset_classes = ["equities", "futures", "options", "currencies"]
            if config["asset_class"] not in valid_asset_classes:
                errors.append(f"Invalid asset class: {config['asset_class']}. Must be one of {valid_asset_classes}")
        
        # Validate strategy type
        if "strategy_type" in config:
            valid_strategy_types = [
                "mean_reversion", "momentum", "arbitrage", "trend_following", 
                "breakout", "options_spread", "forex_carry", "volatility"
            ]
            if config["strategy_type"] not in valid_strategy_types:
                errors.append(f"Invalid strategy type: {config['strategy_type']}. Must be one of {valid_strategy_types}")
        
        # Validate symbol format based on asset class
        if "symbol" in config and "asset_class" in config:
            symbol = config["symbol"]
            asset_class = config["asset_class"]
            
            if asset_class == "currencies":
                if len(symbol) != 6 or not symbol.endswith("INR"):
                    errors.append(f"Invalid currency symbol format: {symbol}. Should be 6 characters ending with INR (e.g., USDINR)")
            elif asset_class in ["futures", "options"]:
                if len(symbol) < 6 or len(symbol) > 12:
                    errors.append(f"Invalid derivative symbol format: {symbol}. Symbol length should be between 6-12 characters")
        
        # Validate parameters based on strategy type
        if "strategy_type" in config:
            strategy_type = config["strategy_type"]
            
            if strategy_type == "options_spread":
                required_params = ["leg1_strike", "leg2_strike", "leg1_type", "leg2_type"]
                for param in required_params:
                    if param not in config:
                        errors.append(f"Missing required parameter for options spread: {param}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }


# Singleton instance
version_control_engine = VersionControlEngine()