import { defineStore } from 'pinia'
import axios from 'axios'

import { apiURL } from '@/stores/index'
import { useMealsStore } from '@/stores/meals'
import { usePeopleStore } from '@/stores/people'
import { usePurchaseStore } from '@/stores/purchase'
import { useResponsibilityStore } from '@/stores/responsibility'
import { useSecurityMessageStore } from '@/stores/securitymessage'
import { useTimeOffStore } from '@/stores/timeoff'
import { useUserStore } from '@/stores/user'
import { useWorkflowsStore } from '@/stores/workflows'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('user-token') || '',
    status: '',
  }),

  getters: {
    isAuthenticated: state => !!state.token
  },

  actions: {
    // Log in with username and password
    authWithUsername(user: {username: string, password: string}) {
      return this.authenticate(user, `${ apiURL }api/api-token-auth-password/`)
    },
    // Log in with Microsoft Azure SSO
    authWithMicrosoft(
      user: { username: string, firstName: string, lastName: string }
    ) {
      return this.authenticate(user, `${ apiURL }api/api-token-auth/`)
    },
    authenticate(
      user: { username: string, password: string } |
        { username: string, firstName: string, lastName: string },
      url: string
    ): Promise<string> {
      return new Promise((resolve, reject) => {
        this.status = 'loading'
        axios({url: url, data: user, method: 'POST'})
          .then((resp) => {
            const token = resp.data.token
            localStorage.setItem('user-token', token)
            axios.defaults.headers.common['Authorization'] = `Token ${token}`
            this.status = 'success'
            this.token = token
            // you have your token, now log in your user :)
            const userStore = useUserStore()
            userStore.userRequest()
              .catch(err => console.log(err))
            resolve(token)
          })
        .catch(err => {
          this.status = 'error'
          // if the request fails, remove any possible user token
          localStorage.removeItem('user-token')
          reject(err)
        })
      })
    },
    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        localStorage.removeItem('user-token')
        const mealsStore = useMealsStore()
        const peopleStore = usePeopleStore()
        const purchaseStore = usePurchaseStore()
        const responsibilityStore = useResponsibilityStore()
        const securityMessageStore = useSecurityMessageStore()
        const timeOffStore = useTimeOffStore()
        const userStore = useUserStore()
        const workflowsStore = useWorkflowsStore()
        mealsStore.authLogout()
          .catch(err => console.log(err))
        peopleStore.authLogout()
          .catch(err => console.log(err))
        // TODO: Uncomment these when the modules are ready
        // dispatch('performanceReviewModule/authLogout', null, { root: true })
        //   .catch(err => console.log(err))
        purchaseStore.authLogout()
          .catch(err => console.log(err))
        responsibilityStore.authLogout()
          .catch(err => console.log(err))
        securityMessageStore.authLogout()
          .catch(err => console.log(err))
        // dispatch('teleworkModule/authLogout', null, { root: true })
        //   .catch(err => console.log(err))
        timeOffStore.authLogout()
          .catch(err => console.log(err))
        userStore.authLogout()
          .catch(err => console.log(err))
        workflowsStore.authLogout()
          .catch(err => console.log(err))

        resolve('Successfully logged user out')
      })
    }
  }
})
