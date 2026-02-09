describe('Market Ticker and Dashboard Cards', () => {
  beforeEach(() => {
    cy.login('trader');
    cy.visit('/');
    cy.waitForAppDataLoad();
  });

  it('shows 4 ticker lanes horizontally', () => {
    cy.get('span').contains('LIVE MARKET').should('be.visible');
    cy.contains('NSE').should('be.visible');
    cy.contains('BSE').should('be.visible');
    cy.contains('MCX').should('be.visible');
    cy.contains('Metals').should('be.visible');
  });

  it('shows Currencies and New IPOs cards', () => {
    cy.contains('Currencies').should('be.visible');
    cy.contains('FX PAIRS').should('be.visible');
    cy.contains('New IPOs').should('be.visible');
    cy.contains('LISTINGS').should('be.visible');
  });
})
