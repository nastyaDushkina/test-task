//import VueTheMask from 'vue-the-mask'
//Vue.use(VueTheMask)

Vue.component('product-card', {
  props: {
    premium: {
      type: Boolean,
      required: true
    }
  },
  template: `
    <div class="container-products">
      <select-filter :premium="premium" @filter-cart="filterCart"></select-filter>
      <transition-group name="slide-fade" tag="ul" class="list-products">
        <li
        v-for="(product, index) in products" v-bind:key="(product, index)"
        class="products-item">
          <button v-on:click="delItem(index)" class="products-item_delete"></button>
          <a href="" class="product">
            <img :src="product.url" :alt="product.name" class="product-img" />
            <div class="product-inf">
              <h2 class="product-name">{{ product.name }}</h2>
              <p class="product-descr">{{ product.descr }}</p>
              <div class="product-price"><span class="product-price_value">{{ product.price }}</span> руб.</div>
            </div>
          </a>
        </li>
      </transition-group>
      <product-form :premium="premium" @add-item="addItem"></product-form>
    </div>
   `,

  data() {
    return {
      show: true,
      products: [],
    }
  },

  methods: {
    addToCart() {
      this.$emit('product-add', this);
    },
    addItem(product) {
      this.products.push(product);
      this.filterCart(sortDefault);
      const select = document.querySelector('#select-filter').getElementsByTagName('option');
      for (let i = 0; i < select.length; i++) {
          if (select[i].value === 'no') select[i].selected = true;
      }
      this.saveToLocalStorageCart();
    },
    delItem: function(index) {
      this.products.splice(index, 1);

      this.saveToLocalStorageCart();
      let cartLocalStorage = JSON.parse(localStorage.getItem("products"));
      if (cartLocalStorage.length == 0) {
        localStorage.removeItem("products");
      }
    },
    saveToLocalStorageCart() {
      localStorage.removeItem("products");
      localStorage.setItem("products", JSON.stringify(this.products));

    },
    cartLocalStorage() {
      if (localStorage.getItem("products")) {
        let cartLocalStorage = JSON.parse(localStorage.getItem("products"));
        return cartLocalStorage;
      } else {
        return [];
      }
    },
    filterCart(param) {
      console.log(param);
      switch(param) {
        case 'priceUp': return this.products.sort(sortPriceUp);
        case 'priceDown': return this.products.sort(sortPriceDown);
        default: return this.products.sort(sortDefault);
      }
    }
  },
  mounted() {
    this.products = this.cartLocalStorage();
  },
})

Vue.component("modal", {
  template: `
  <transition name="modal">
    <div class="modal-mask" id="modal">
      <div class="modal-wrapper">Товар успешно добавлен!</div>
      <button class="modal-button" @click="$emit('close')">&times;</button>
    </div>
  </transition>`,
});

Vue.component('select-filter', {
  props: ['value'],

  template: `
    <select id="select-filter" name="select" v-model="selected" :value="value" v-on:change="$emit('filter-cart', $event.target.value)" class="app-filter">
      <option value="no" selected>По умолчанию</option>
      <option value="priceUp">По возрастанию цены</option>
      <option value="priceDown">По убыванию цены</option>
    </select>`,

  model: {
    prop: 'value',
    event: 'change'
  },

  data() {
    return {
      selected: 'no',
    }
  },
})

Vue.component('product-form', {
  props: {
    premium: {
      type: Boolean,
      required: true
    }
  },

  template: `
    <div class="form">
      <form class="add-form" @submit.prevent="onSubmit">
        <label for="destignation" class="form-field_name field-required">Наименование товара</label>
        <input v-model="name" type="text" name="designation" id="destignation" class="form-designation form-field" placeholder="Введите наименование товара">
        <label for="description" class="form-field_name">Описание товара</label>
        <textarea v-model="descr" name="description" id="description" class="form-description form-field" placeholder="Введите описание товара"></textarea>
        <label for="url" class="form-field_name field-required">Ссылка на изображение товара</label>
        <input v-model="url" type="url" name="url" id="url" class="form-designation form-field" placeholder="Введите ссылку">
        <label for="price" placeholder="Введите цену" class="form-field_name  field-required">Цена товара</label>
        <input v-model="price" type="number" name="price" id="price" min="0" class="form-designation form-field">
        <button type="submit" class="add-form_btn" disabled :disabled="!(name && url && price) ? true : false"><span class="add-form_button">Добавить товар</span></button>
      </form>
      <modal v-if="showModal" @close="showModal = false"></modal>
    </div>
  `,

  data() {
    return {
      name: this.name,
      descr: this.descr,
      url: this.url,
      price: this.price,
      id: 0,
      showModal: false,
    }
  },

  methods: {
    onSubmit() {
      this.errors = [];
      if(this.name  && this.url && this.price) {
        this.showModal = true;
        if (!this.descr) {
          this.descr = 'Описание отсутствует'
        }
        let newProduct = {
          id: this.id,
          name: this.name,
          descr: this.descr,
          url: this.url,
          price: this.price
        }
        this.$emit('add-item', newProduct)
        this.id++
        this.name = null
        this.descr = null
        this.url = null
        this.price = null
        setTimeout(this.hideModal, 5000);
      }
    },
    hideModal() {
      this.showModal = false;
    }
  },
})

var app = new Vue({
  el: '#app',
  data: {
    premium: true,
    products: [],
    current: [],
    flag: true,
  },

  methods: {
    addProduct(product) {
      this.products.push(product);
    }
  }
})

var sortPriceUp = function(d1, d2) {
  return (Number(d1.price) > Number(d2.price)) ? 1 : -1;
}

var sortPriceDown = function(d1, d2) {
  return (Number(d1.price) < Number(d2.price)) ? 1 : -1;
}

var sortDefault = function(d1, d2) {
  return (Number(d1.id) > Number(d2.id)) ? 1 : -1;
}

