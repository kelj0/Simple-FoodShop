Vue.component('modal',{
    template: '#modal-template'
  })
Vue.use(VueScrollTo)

window.app = new Vue({
    el: '#app',
    components: {
        VueGallerySlideshow
    },
    data: {
        gindex: null,
        glavnaimgs: [
        'img/glavna_jela/pizza.jpg',
        'img/glavna_jela/odojak.jpg',
        'img/glavna_jela/zagrebacki.jpg',
        'img/glavna_jela/bijelo_meso.jpg'
        ],
        dindex: null,
        desertiimgs: [
        'img/deserti/kremsnite.jpg',
        'img/deserti/ledeni_vjetar.jpg',
        'img/deserti/madarica.jpg',
        'img/deserti/princes_krafne.jpg'
        ],
        pindex: null,
        pekarskiimgs: [
        'img/pekarski_proizvodi/buhtla.jpg',
        'img/pekarski_proizvodi/kruh.jpg',
        'img/pekarski_proizvodi/krafna.jpg',
        'img/pekarski_proizvodi/slanac.jpg'
        ],
        sticky: null,
        showModal: false,
        food: null,
        cardBox: [],
        basketPrice: 0
      },
    delimiters: ['[[',']]'],
    methods: {
        expandNav() {
            var x = document.getElementById("navbar");
            if (x.className === "topnav" || x.className ==="topnav sticky") {
              x.className += " responsive";
            }
            else if(x.className === "topnav sticky responsive"){
                x.className = "topnav sticky";
            }
            else {
              x.className = "topnav";
            }
        },
        stickNav(){
            var navbar = document.getElementById("navbar");
            if (window.pageYOffset >= this.sticky) {
                navbar.classList.add("sticky")
                document.getElementById("return-to-top").style.visibility= "visible";
                document.getElementById("return-to-top").style.opacity = 1;
            } else {
                navbar.classList.remove("sticky");
                document.getElementById("return-to-top").style.display= "hidden";
                document.getElementById("return-to-top").style.opacity = 0;
            }
        },
        ajdustNav(){
            var i = document.getElementById("landingVid")
            var s = document.getElementById("navbar")
            this.sticky = i.clientHeight-48;
            if(window.pageYOffset < this.sticky){
                s.setAttribute('style',`top: ${this.sticky}px`);
            }else{
                s.setAttribute('style',`top: 0px`);

            }
        },
        handleSubmit(){
            if(document.getElementById("testName").checked) {
                document.getElementById('testNameHidden').disabled = true;
            };
            let form = document.getElementById("fform");
            form.action = "http://www.fulek.com/VUA/SUPIT/ContactUs";
            form.method = 'POST';
            form.submit();
        },
        baskedHandler(data,what){
            if(what=='add'){
                console.log(`Add ${data.name} to basked`)
                var found=false;
                for (let i = 0; i < this.cardBox.length; i++) {
                    if(this.cardBox[i].name==data.name){
                        this.cardBox[i].amount+=1
                        found=true;
                        this.basketPrice += data.price;
                        break;
                    }                    
                }
                if(!found){
                    this.cardBox.push({'name':data.name,'price':data.price,'amount':1});
                    this.basketPrice += data.price;
                }
            }else if(what=='remove'){
                for (let i = 0; i < this.cardBox.length; i++) {
                    if(this.cardBox[i].name==data.name){
                        if(this.cardBox[i].amount==1){
                            this.basketPrice -= (data.price)
                            this.cardBox.splice(i,1)
                        }else{
                            this.cardBox[i].amount-=1
                            this.basketPrice -= (data.price)
                        }
                        break;
                    }
                }
            }else{
                this.cardBox.forEach(element => {
                        this.removeFood(element,element.amount)
                })
                this.basketPrice = 0
                this.cardBox = []
            }
            //https://stackoverflow.com/a/28515376/9564839
            this.basketPrice = Math.round(this.basketPrice*100)/100
        },
        removeFood(data,amountToRemove=1) {
            axios
              .post('/alterFood',{'name':data.name,'subclass':data.subclass,'what':'remove','number':amountToRemove})
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
        respIcoForm(){
            if(window.innerWidth < 786){
                document.getElementById("icon").className="fab fa-angellist fa-3x";
                document.getElementsByName("sicons").forEach(element=>{
                    var el = element.classList[2];
                    element.classList.remove(el)
                    element.classList.add("fa-2x");
                })
                console.log("Smaller than 786");
            }
            else if(window.innerWidth < 1200){
                document.getElementById("icon").className="fab fa-angellist fa-8x";
                document.getElementsByName("sicons").forEach(element=>{
                    var el = element.classList[2];
                    element.classList.remove(el)
                    element.classList.add("fa-3x");
                })
                console.log("Smaller than 1200");
            }else{
                document.getElementById("icon").className="fab fa-angellist fa-10x";
                document.getElementsByName("sicons").forEach(element=>{
                    var el = element.classList[2];
                    element.classList.remove(el)
                    element.classList.add("fa-5x");
                })
                console.log("Bigger than 1200");
            }
        }
    },
    created() {
        window.addEventListener('scroll', this.stickNav),
        window.addEventListener('scroll', this.ajdustNav),
        window.addEventListener("mousemove", this.ajdustNav),
        window.addEventListener("resize", this.ajdustNav),
        window.addEventListener('resize', this.respIcoForm),
        this.sticky = document.getElementById("landingVid").clientHeight-48,
        document.getElementById("navbar").setAttribute('style',`top: ${this.sticky}px`),
        this.updateFood(),
        this.ajdustNav()
    },
    mounted(){
        this.ajdustNav(),
        this.respIcoForm()
    },
    destroyed(){
        window.removeEventListener('scroll', this.stickNav),
        window.removeEventListener('scroll', this.ajdustNav),
        window.removeEventListener("mousemove", this.ajdustNav),
        window.removeEventListener("resize", this.ajdustNav),
        window.removeEventListener('resize', this.respIcoForm)
    }
})