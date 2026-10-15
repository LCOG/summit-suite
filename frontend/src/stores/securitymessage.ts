import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from '@/stores/index'
import { SecurityMessage, ViewedSecurityMessageCreate } from '@/types'

export const useSecurityMessageStore = defineStore('securitymessage', {
  state: () => ({
    latestSecurityMessage: {} as SecurityMessage,
    viewedSecurityMessages: [],
    viewedLatestSecurityMessage: false
  }),

  getters: {},

  actions: {
    getLatestSecurityMessage(): Promise<SecurityMessage> {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/securitymessage/get_latest_security_message` })
          .then(resp => {
            this.latestSecurityMessage = resp.data
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting latest security message', e)
          });
      })
    },
    getViewedLatestSecurityMessage() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/viewedsecuritymessage/employee_viewed_latest_security_message` })
          .then(resp => {
            this.viewedLatestSecurityMessage = resp.data
            resolve('Successfully got viewed latest security message')
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting viewed latest security message', e)
          });
      })
    },
    getViewedSecurityMessages() {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/viewedsecuritymessage` })
          .then(resp => {
            this.viewedSecurityMessages = resp.data.results
            resolve('Successfully got viewed security messages')
          })
          .catch(e => {
            handlePromiseError(reject, 'Error getting viewed security messages', e)
          });
      })
    },
    setViewedSecurityMessage(viewedSecurityMessage: ViewedSecurityMessageCreate) {
      return new Promise((resolve, reject) => {
        axios({ url: `${ apiURL }api/v1/viewedsecuritymessage`, data: viewedSecurityMessage, method: 'POST' })
          .then(() => {
            Promise.all([
              this.getViewedLatestSecurityMessage(),  this.getViewedSecurityMessages()
            ])
            .then(() => {
              resolve('Successfully marked a security message as viewed')
            })
            .catch(e => {
              handlePromiseError(reject, 'Error getting viewed latest security message ater marking one as viewed', e)
            })
          })
          .catch(e => {
            handlePromiseError(reject, 'Error marking a security message as viewed', e)
          });
      })
    },
    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    }
  }
});
