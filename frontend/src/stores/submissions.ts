import axios from 'axios'
import { defineStore } from 'pinia'

import { apiURL, handlePromiseError } from 'src/stores/index'
import {
  MileageSubmissionCreate,
  MileageSubmissionRetrieve,
  SubmissionRetrieve
} from 'src/types'

export const useSubmissionsStore = defineStore('submissions', {
  state: () => ({
    mileageSubmissions: [] as Array<MileageSubmissionRetrieve>,
    submissions: [] as Array<SubmissionRetrieve>
  }),

  actions: {
    getMileageSubmissions() {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission`
        })
          .then(resp => {
            this.mileageSubmissions = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting mileage submissions',
              e
            )
          })
      })
    },

    createMileageSubmission(data: MileageSubmissionCreate) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission`,
          method: 'POST',
          data
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error creating mileage submission',
              e
            )
          })
      })
    },

    approveMileageSubmission(pk: number) {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/mileage-submission/${pk}/approve`,
          method: 'PUT',
          data: {}
        })
          .then(resp => {
            resolve(resp.data)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error approving mileage submission',
              e
            )
          })
      })
    },

    getSubmissions() {
      return new Promise((resolve, reject) => {
        axios({
          url: `${apiURL}api/v1/submission`
        })
          .then(resp => {
            this.submissions = resp.data.results
            resolve(resp.data.results)
          })
          .catch(e => {
            handlePromiseError(
              reject,
              'Error getting submissions',
              e
            )
          })
      })
    },

    authLogout() {
      return new Promise((resolve) => {
        this.$reset()
        resolve('Successfully triggered logout')
      })
    }
  }
})
