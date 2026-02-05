describe('Simple Login Test', () => {
    it('should login and navigate to home', () => {
        cy.visit('/login');
        
        // Click on the trader login button
        cy.get('[data-testid="login-trader"]').click();
        
        // Should redirect to home page
        cy.url().should('eq', 'http://localhost:3000/');
        
        // Should see the main heading
        cy.get('h1').should('be.visible');
    });
    
    it('should login using command and navigate to trading', () => {
        cy.login('trader');
        cy.visit('/trading');
        
        // Should see the trading hub heading
        cy.get('h1').should('contain', 'Trading Hub');
    });
});