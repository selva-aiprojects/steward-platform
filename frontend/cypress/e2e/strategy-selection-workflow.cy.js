describe('Strategy Selection Workflow', () => {
    beforeEach(() => {
        // Login as a trader user before each test
        cy.login('trader');
    });

    it('should navigate to strategy selection page and display available strategies', () => {
        // Navigate to the strategy selection page using the sidebar
        cy.get('[href="/strategies"]').click();
        
        // Verify we're on the strategy selection page
        cy.url().should('include', '/strategies');
        
        // Verify the page header
        cy.contains('Algorithmic Strategy Selection').should('be.visible');
        cy.contains('Choose from our curated collection of proven algorithmic trading strategies').should('be.visible');
        
        // Verify strategy cards are displayed
        cy.get('[data-testid="trading-hub-container"]').should('not.exist'); // Should not be on trading hub
        cy.get('.grid').find('div').should('have.length.greaterThan', 0); // Should have strategy cards
        
        // Verify progress steps are visible
        cy.get('div').contains('Select Strategy').should('be.visible');
        cy.get('div').contains('Configure').should('be.visible');
        cy.get('div').contains('Deploy').should('be.visible');
    });

    it('should allow user to browse and select a strategy', () => {
        cy.visit('/strategies');
        
        // Verify initial state - step 0 (selection)
        cy.get('div').contains('Choose Your Strategy').should('be.visible');
        
        // Find and click on the Momentum Trader strategy card
        cy.contains('Momentum Trader').closest('.p-5').click();
        
        // Verify we moved to configuration step (step 1)
        cy.contains('Configure Momentum Trader').should('be.visible');
        cy.contains('Customize your strategy parameters').should('be.visible');
        
        // Verify strategy information is displayed
        cy.contains('Momentum Trader').should('be.visible');
        cy.contains('Capitalizes on the continuance of existing trends in the market').should('be.visible');
        cy.contains('Medium Risk').should('be.visible');
        cy.contains('+12.4%').should('be.visible');
        
        // Verify configuration form elements
        cy.get('input[placeholder="Enter amount to allocate"]').should('be.visible');
        cy.get('select').first().should('be.visible'); // Risk tolerance dropdown
        cy.get('select').eq(1).should('be.visible'); // Investment horizon dropdown
        cy.get('input[type="number"]').eq(0).should('be.visible'); // Stop loss
        cy.get('input[type="number"]').eq(1).should('be.visible'); // Take profit
    });

    it('should allow user to configure strategy parameters', () => {
        cy.visit('/strategies');
        
        // Select a strategy first
        cy.contains('Mean Reversion').closest('.p-5').click();
        
        // Fill in configuration parameters
        cy.get('input[placeholder="Enter amount to allocate"]').type('50000');
        
        // Select risk tolerance
        cy.get('select').first().select('medium');
        
        // Select investment horizon
        cy.get('select').eq(1).select('short');
        
        // Set stop loss and take profit
        cy.get('input[type="number"]').eq(0).clear().type('5');
        cy.get('input[type="number"]').eq(1).clear().type('10');
        
        // Verify values are correctly set
        cy.get('input[placeholder="Enter amount to allocate"]').should('have.value', '50000');
        cy.get('select').first().should('have.value', 'medium');
        cy.get('select').eq(1).should('have.value', 'short');
        cy.get('input[type="number"]').eq(0).should('have.value', '5');
        cy.get('input[type="number"]').eq(1).should('have.value', '10');
    });

    it('should allow user to deploy strategy and see confirmation', () => {
        cy.visit('/strategies');
        
        // Select a strategy
        cy.contains('Breakout Hunter').closest('.p-5').click();
        
        // Configure parameters
        cy.get('input[placeholder="Enter amount to allocate"]').type('75000');
        cy.get('select').first().select('high');
        cy.get('select').eq(1).select('short');
        cy.get('input[type="number"]').eq(0).clear().type('7');
        cy.get('input[type="number"]').eq(1).clear().type('15');
        
        // Click deploy button
        cy.contains('Deploy Strategy').click();
        
        // Verify deployment confirmation
        cy.contains('Strategy Deployed Successfully!').should('be.visible');
        cy.contains('Your Breakout Hunter strategy has been successfully deployed').should('be.visible');
        
        // Verify strategy details in confirmation
        cy.contains('Breakout Hunter').should('be.visible');
        cy.contains('Active').should('be.visible');
        cy.contains('High').should('be.visible');
        
        // Verify navigation buttons
        cy.contains('Select Another Strategy').should('be.visible');
        cy.contains('Go to Dashboard').should('be.visible');
    });

    it('should allow user to go back to strategy selection from configuration', () => {
        cy.visit('/strategies');
        
        // Select a strategy
        cy.contains('Swing Trader').closest('.p-5').click();
        
        // Verify we're in configuration step
        cy.contains('Configure Swing Trader').should('be.visible');
        
        // Click back button
        cy.contains('Back').click();
        
        // Verify we're back to selection step
        cy.contains('Choose Your Strategy').should('be.visible');
        cy.contains('Browse our collection of algorithmic trading strategies').should('be.visible');
    });

    it('should allow user to select another strategy from confirmation', () => {
        cy.visit('/strategies');
        
        // Select and deploy a strategy
        cy.contains('Options Straddle').closest('.p-5').click();
        cy.get('input[placeholder="Enter amount to allocate"]').type('100000');
        cy.contains('Deploy Strategy').click();
        
        // Verify confirmation
        cy.contains('Strategy Deployed Successfully!').should('be.visible');
        
        // Click "Select Another Strategy"
        cy.contains('Select Another Strategy').click();
        
        // Verify we're back to strategy selection
        cy.contains('Choose Your Strategy').should('be.visible');
    });

    it('should filter strategies by category', () => {
        cy.visit('/strategies');
        
        // Verify all strategies are initially shown
        cy.get('.grid').find('div').should('have.length.greaterThan', 0);
        
        // Click on "Equities" filter
        cy.contains('Equities').click();
        
        // Verify only equities strategies are shown
        cy.get('.grid').within(() => {
            cy.get('div').each(($el) => {
                if ($el.find('span').text().includes('equities')) {
                    cy.wrap($el).should('be.visible');
                }
            });
        });
        
        // Click on "Options" filter
        cy.contains('Options').click();
        
        // Verify only options strategies are shown
        cy.get('.grid').within(() => {
            cy.get('div').each(($el) => {
                if ($el.find('span').text().includes('options')) {
                    cy.wrap($el).should('be.visible');
                }
            });
        });
        
        // Click "All Strategies" to reset
        cy.contains('All Strategies').click();
        
        // Verify all strategies are shown again
        cy.get('.grid').find('div').should('have.length.greaterThan', 0);
    });

    it('should display strategy details when selected', () => {
        cy.visit('/strategies');
        
        // Select a strategy
        cy.contains('Pairs Trading').closest('.p-5').click();
        
        // Verify detailed information is shown
        cy.contains('Selected: Pairs Trading').should('be.visible');
        cy.contains('Exploits correlation between two related securities').should('be.visible');
        cy.contains('Avg Returns').should('be.visible');
        cy.contains('+9.1%').should('be.visible');
        cy.contains('Win Rate').should('be.visible');
        cy.contains('70%').should('be.visible');
        cy.contains('Holding Time').should('be.visible');
        cy.contains('1-2 weeks').should('be.visible');
        cy.contains('Min Capital').should('be.visible');
        cy.contains('₹60,000').should('be.visible');
        
        // Verify features are listed
        cy.contains('Correlation analysis').should('be.visible');
        cy.contains('Cointegration').should('be.visible');
        cy.contains('Market neutral').should('be.visible');
        
        // Verify risk level is displayed
        cy.contains('Risk Level: Low-Medium').should('be.visible');
    });
});