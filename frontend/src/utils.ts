import { RouteLocationNormalizedLoaded } from 'vue-router'

import { handlePromiseError } from 'src/stores'
import { useAuthStore } from 'src/stores/auth'
import { useUserStore } from 'src/stores/user'

const authStore = useAuthStore()
const userStore = useUserStore()

export function getRouteParam(
  route: RouteLocationNormalizedLoaded, param: string
): string | null {
  if (!route || route.params[param] == undefined) {
    return null
  } else {
    return typeof route.params[param] == 'string' ? route.params[param] :
      route.params[param][0]
  }
}

export function getRoutePk(route: RouteLocationNormalizedLoaded) {
  return getRouteParam(route, 'pk')
}

export function getRouteQuery(
  route: RouteLocationNormalizedLoaded, query: string
): string | null {
  if (!route || route.query[query] == undefined) {
    return null
  } else {
    return route.query[query] as string
  }
}

export function getCurrentUser(): Promise<any> {
  // Get the current user from the store. If the user is not authenticated,
  // reject the promise.
  return new Promise((resolve, reject) => {
    if (!authStore.isAuthenticated) {
      reject('User is not authenticated')
    } else if (userStore.isProfileLoaded) {
      resolve(userStore.getEmployeeProfile)
    } else {
      userStore.userRequest()
        .then(() => {
          resolve(userStore.getEmployeeProfile)
        })
        .catch(e => {
          handlePromiseError(reject, 'Error getting user from store', e)
        })
    }
  })
}

export function isInteger(str: string): boolean {
  return /^\+?(0|[1-9]\d*)$/.test(str);
}
