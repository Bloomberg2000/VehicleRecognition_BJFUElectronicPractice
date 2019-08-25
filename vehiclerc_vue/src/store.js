import Vue from 'vue'
import Vuex from 'vuex'
import imagePath from '@/assets/js/image.js'
import createVuexAlong from 'vuex-along'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    imageStyle: imagePath,
    currentUserID: ""
  },
  mutations: {
    userChange(state, userID) {
      state.currentUserID = userID;
    }
  },
  actions: {},
  plugins: [createVuexAlong()]
})
