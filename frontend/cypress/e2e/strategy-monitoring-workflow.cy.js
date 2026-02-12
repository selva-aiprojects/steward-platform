describe('Strategy Progress Monitoring in Portfolio', () => {
    beforeEach(() => {
        // Login as a trader user before each test
        cy.login('trader');
    });

    it('should display active strategies in Trading Hub after deployment', () => {
        // First, deploy a strategy using the strategy selection page
        cy.visit('/strategies');
        
        // Select and deploy a strategy
        cy.contains('Momentum Trader').closest('.p-5').click();
        cy.get('input[placeholder="Enter amount to allocate"]').type('50000');
        cy.get('select').first().select('medium');
        cy.get('select').eq(1).select('short');
        cy.get('input[type="number"]').eq(0).clear().type('5');
        cy.get('input[type="number"]').eq(1).clear().type('10');
        cy.contains('Deploy Strategy').click();
        
        // Verify deployment confirmation
        cy.contains('Strategy Deployed Successfully!').should('be.visible');
        
        // Navigate to Trading Hub
        cy.visit('/trading');
        
        // Wait for data to load
        cy.waitForAppDataLoad();
        
        // Verify the deployed strategy appears in the active strategies section
        cy.contains('Active Strategies').should('be.visible');
        cy.contains('Momentum Trader').should('be.visible');
        
        // Verify strategy details are shown
        cy.contains('RUNNING').should('be.visible');
        cy.contains('Symbol:').should('be.visible');
        cy.contains('PnL:').should('be.visible');
        cy.contains('Trades:').should('be.visible');
    });

    it('should display strategy status and performance in Portfolio page', () => {
        // Navigate to Portfolio page
        cy.visit('/portfolio');
        
        // Wait for data to load
        cy.waitForAppDataLoad();
        
        // Verify portfolio page elements
        cy.contains('Portfolio Overview').should('be.visible');
        
        // Look for strategy-related elements
        cy.contains('Strategy Status').should('be.visible');
        cy.contains('Active Strategies').should('be.visible');
        
        // Verify strategy status indicators
        cy.get('[data-testid="algo-status"]').should('be.visible');
        cy.contains('Algo Engine:').should('be.visible');
    });

    it('should show strategy performance metrics in Investment Dashboard', () => {
        // Navigate to Investment Dashboard
        cy.visit('/investment');
        
        // Wait for data to load
        cy.waitForAppDataLoad();
        
        // Verify investment dashboard elements
        cy.contains('Investment Dashboard').should('be.visible');
        
        // Look for strategy-related sections
        cy.contains('Strategy Performance').should('be.visible');
        cy.contains('Active Investment Strategy').should('be.visible');
        
        // Verify strategy launch button exists
        cy.contains('Quick Launch Strategy').should('be.visible');
    });

    it('should allow viewing strategy details from Portfolio page', () => {
        // Navigate to Portfolio page
        cy.visit('/portfolio');
        
        // Wait for data to load
        cy.waitForAppDataLoad();
        
        // Look for strategy management section
        cy.contains('Manage Strategy in Trading Hub').should('be.visible');
        
        // Verify strategy status information
        cy.contains('Your investment strategy is currently running').should('be.visible');
        
        // Click on strategy management link to go to Trading Hub
        cy.contains('Manage Strategy in Trading Hub').click();
        
        // Verify we're on Trading Hub page
        cy.url().should('include', '/trading');
        cy.contains('Trading Hub').should('be.visible');
    });

    it('should display strategy performance in Reports section', () => {
        // Navigate to Reports page
        cy.visit('/reports');
        
        // Wait for data to load
        cy.waitForAppDataLoad();
        
        // Look for strategy performance section
        cy.contains('Strategy Engine Performance').should('be.visible');
        
        // Verify algorithmic vs manual performance comparison
        cy.contains('Algorithmic vs Manual Performance').should('be.visible');
        
        // Verify performance metrics are displayed
        cy.contains('Algo Smart Decision Logic').should('be.visible');
    });

    it('should maintain strategy state after page refresh', () => {
        // Deploy a strategy first
        cy.visit('/strategies');
        cy.contains('Mean Reversion').closest('.p-5').click();
        cy.get('input[placeholder="Enter amount to allocate"]').type('25000');
        cy.contains('Deploy Strategy').click();
        cy.contains('Strategy Deployed Successfully!').should('be.visible');
        
        // Navigate to Trading Hub
        cy.visit('/trading');
        cy.waitForAppDataLoad();
        
        // Verify strategy is active
        cy.contains('Active Strategies').should('be.visible');
        cy.contains('Mean Reversion').should('be.visible');
        
        // Refresh the page
        cy.reload();
        
        // Wait for data to reload
        cy.waitForAppDataLoad();
        
        // Verify the strategy is still shown as active
        cy.contains('Active Strategies').should('be.visible');
        cy.contains('Mean Reversion').should('be.visible');
        cy.contains('RUNNING').should('be.visible');
    });

    it('should show strategy performance charts in Investment Reports', () => {
        // Navigate to Investment Reports
        cy.visit('/reports/investment');
        
        // Wait for data to load
        cy.waitForAppDataLoad();
        
        // Verify investment reports page elements
        cy.contains('Investment Reports').should('be.visible');
        
        // Look for strategy performance charts
        cy.contains('Strategy Performance Analytics').should('be.visible');
        
        // Verify algo performance metrics
        cy.contains('Algo Performance').should('be.visible');
        cy.contains('Manual Performance').should('be.visible');
        
        // Verify performance comparison chart exists
        cy.get('svg').should('exist'); // Recharts generates SVG elements
    });

    it('should allow strategy management from multiple pages', () => {
        // Deploy a strategy first
        cy.visit('/strategies');
        cy.contains('Breakout Hunter').closest('.p-5').click();
        cy.get('input[placeholder="Enter amount to allocate"]').type('75000');
        cy.contains('Deploy Strategy').click();
        cy.contains('Strategy Deployed Successfully!').should('be.visible');
        
        // Test strategy management from Trading Hub
        cy.visit('/trading');
        cy.waitForAppDataLoad();
        cy.contains('Breakout Hunter').should('be.visible');
        
        // Test strategy status in Portfolio
        cy.visit('/portfolio');
        cy.waitForAppDataLoad();
        cy.contains('Active').should('be.visible');
        
        // Test strategy performance in Investment Dashboard
        cy.visit('/investment');
        cy.waitForAppDataLoad();
        cy.contains('Active Investment Strategy').should('be.visible');
    });
});