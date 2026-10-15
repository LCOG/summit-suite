import { defineStore } from '#q-app'
import { createPinia } from 'pinia'
import { Router } from 'vue-router'
import { AxiosError } from 'axios'

/*
 * When adding new properties to stores, you should also
 * extend the `PiniaCustomProperties` interface.
 * @see https://pinia.vuejs.org/core-concepts/plugins.html#typing-new-store-properties
 */
declare module 'pinia' {
  export interface PiniaCustomProperties {
    readonly router: Router
  }
}

/*
 * If not building with SSR mode, you can
 * directly export the Store instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Store instance.
 */

export default defineStore((/* { ssrContext } */) => {
  const pinia = createPinia()

  // You can add Pinia plugins here
  // pinia.use(SomePiniaPlugin)

  return pinia
})

export function handlePromiseError(
  reject: (reason?: any) => void, message: string, error?: AxiosError
) {
  let reason: string | undefined
  if (error) {
    reason = error.message
    if (error.response && error.response.data && error.response.data) {
      reason = error.response.data as string
    }
  }
  let errorMessage: string
  if (reason) {
    errorMessage = `${ message }: ${ reason }`
  } else {
    errorMessage = message
  }
  console.error(errorMessage)
  reject(errorMessage)
}

export const apiURL = import.meta.env.API_URL ?
  import.meta.env.API_URL : 'https://api.team.lcog.org/'
