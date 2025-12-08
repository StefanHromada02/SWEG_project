import {
  APP_INITIALIZER,
  ApplicationConfig,
  importProvidersFrom,
} from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';

import { routes } from './app.routes';
import {KeycloakAngularModule, KeycloakService, KeycloakBearerInterceptor} from 'keycloak-angular';
import {provideAnimations} from '@angular/platform-browser/animations';
import {initializeKeycloak} from './init/keycloak-init.factory';
import { HTTP_INTERCEPTORS } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),

    provideAnimations(),

    // Enable interceptors from DI for Keycloak Bearer token
    provideHttpClient(withInterceptorsFromDi()),

    importProvidersFrom(KeycloakAngularModule),

    // Add Keycloak Bearer Interceptor to automatically add JWT token to requests
    {
      provide: HTTP_INTERCEPTORS,
      useClass: KeycloakBearerInterceptor,
      multi: true,
    },

    {
      provide: APP_INITIALIZER,
      useFactory: initializeKeycloak,
      multi: true,
      deps: [KeycloakService],
    },
  ],
};
