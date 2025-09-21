/**
 * Check if the current domain matches a specific subdomain
 */
function isSubdomain(subdomainName: string): boolean {
  if (typeof window === 'undefined' || !window.location) {
    return false;
  }
  
  const hostname = window.location.hostname
  return hostname.includes(subdomainName)
}

/**
 * Check if the current domain is the portfolio subdomain
 */
export function isPortfolio(): boolean {
  return isSubdomain(import.meta.env.PORTFOLIO_SUBDOMAIN || 'portfolio')
}

/**
 * Check if the current domain is the energy subdomain
 */
export function isEnergy(): boolean {
  return isSubdomain(import.meta.env.ENERGY_SUBDOMAIN || 'energy')
}

/**
 * Site configuration
 */
export const siteConfig = {
  get isPortfolio() {
    return isPortfolio()
  },
  
  get isEnergy() {
    return isEnergy()
  },
  
  get currentSite(): 'main' | 'portfolio' | 'energy' {
    if (isPortfolio()) return 'portfolio'
    if (isEnergy()) return 'energy'
    return 'main'
  }
};