// src/utils/siteConfig.ts

/**
 * Minimal site configuration - just what you need right now
 */

/**
 * Check if the current domain is the portfolio subdomain
 */
export function isPortfolio(): boolean {
    if (typeof window === 'undefined' || !window.location) {
      return false;
    }
    
    const hostname = window.location.hostname;
    return hostname.includes('portfolio');
  }
  
  /**
   * Simple site config with just the essentials
   */
  export const siteConfig = {
    
    // Whether we're on the portfolio site
    get isPortfolio() {
      return isPortfolio();
    }
  };