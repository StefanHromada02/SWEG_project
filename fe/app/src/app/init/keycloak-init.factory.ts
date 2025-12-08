import { KeycloakService } from "keycloak-angular";

export function initializeKeycloak(keycloak: KeycloakService) {
  return () =>
    keycloak.init({
      config: {
        url: 'http://localhost:8080',
        realm: 'social-media-realm',
        clientId: 'frontend',
      },

      initOptions: {
        onLoad: 'check-sso',
        checkLoginIframe: false
      },
      enableBearerInterceptor: true,
      bearerExcludedUrls: ['/assets'],
      // Add backend API to included URLs to ensure token is sent
      bearerPrefix: 'Bearer',
      shouldAddToken: (request) => {
        const { method, url } = request;
        
        // Always add token to backend API requests
        const isBackendUrl = url.includes('localhost:8000') || url.includes('/api/');
        
        // Don't add token to Keycloak or assets URLs
        const isExcluded = url.includes('localhost:8080') || 
                          url.includes('/assets') ||
                          url.includes('keycloak');
        
        return isBackendUrl && !isExcluded;
      }
    });
}
