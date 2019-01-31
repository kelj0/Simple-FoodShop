Vue.component('modal',{
  template: '#modal-template'
})

var v = new Vue({
    el: '#app',
    data() {
      return {
        users: null,
        food: null,
        showModal: false,
        RmorAddquant:1
      }
    },
    delimiters: ['[[',']]'],
    methods: {
      removeUser(data) {
        axios
          .post('/deleteUser',{'username':data.username})
          .then(
              response => (
                console.log("[Response] -> : " + response.data['message']),
                this.updateUsers()
                )
              )
      },
      removeFood(data) {
        axios
          .post('/alterFood',{'name':data.name,'subclass':data.subclass,'what':'remove','number':this.RmorAddquant})
          .then(
            response => (
                console.log(`[${response.data['status']}] -> : ${response.data['message']}`),
                this.updateFood()
                )
              )
      },
      addFood(data) {
        axios
          .post('/alterFood',{'name':data.name,'subclass':data.subclass,'what':'add','number':this.RmorAddquant})
          .then(
            response => (
                console.log(`[${response.data['status']}] -> : ${response.data['message']}`),
                this.updateFood()
                )
              )
      },
      updateFood(){
        axios
          .get('/food')
          .then(response => {this.food = response.data})
      },
      updateUsers(){
        axios
          .get('/users')
          .then(response => this.users = response.data)
          .then(console.log("Users refreshed!"));
      },
      logout(){
        axios
          .get('/logout')
      }
    },
    mounted () {
      this.updateUsers();
      this.updateFood();
      }
    })