<template>
 <page-header>
    <h1 class="title">Welcome to AutoCompleter! </h1>
    <h2 class="subtitle">Probability based model that suggests next word</h2>
 </page-header>


  <div>

      <input class="input is-rounded" 
        v-model="search" 
        @input="onChange"
        @keyup.down="onArrowDown" 
        @keyup.up="onArrowUp" 
        @keyup.enter="onEnter"
        autocomplete="off"
        placeholder="Enter your text here for auto suggestion..."/>

    <ul id="autocomplete-results" v-show="isOpen" class="autocomplete-results">
      <li class="loading" v-if="isLoading">
        Loading Results...
      </li>
      <li v-else v-for="(result, i) in results" :key="i" @click="setResult(result)"
                class="autocomplete-result" :class="{ 'is-active': i === arrowCounter }">
      {{result}}
      </li>
    </ul> 

  <br>
  <br>
  <p><b>Your search query: {{ search }}</b></p>
  </div>

</template>

<script>
// Reference: https://codepen.io/alligatorio/pen/mXRGLg

import PageHeader from "@/components/PageHeader"
import api from "@/backend/api"

export default {
  name: "HomePage",
  components: {PageHeader},
  data() {
    return {
      search: "",
      isOpen: false,
      results: [],
      isLoading: false,
      arrowCounter: -1
    };
  },
  mounted() {
    console.info("mounted")
    document.addEventListener("click", this.handleClickOutside);
  },
  unmounted() {
    document.removeEventListener("click", this.handleClickOutside);
  },
  created() {

  },
  methods: {
    onChange() {
      // Let's warn the parent that a change was made
      this.$emit("input", this.search);

      console.info(event.target.value)
      // console.info("onchange", this.results)

      // Remove spaces in the tokens
      var cleandedQuery = this.search.split(" ").filter(e => e).join(" ")

      this.isLoading = true

      // Backend 
      api.post(process.env.VUE_APP_SUGGESTIONS_API, {text: cleandedQuery})
      .then((res) => {
        this.isLoading = false
        this.results = res.data.tokens
        console.info("suggestions", this.results)
      })
      .catch((err) => console.error(err))
      this.isOpen = true
    },
    onArrowDown() {
      if (this.arrowCounter < this.results.length) {
        this.arrowCounter = this.arrowCounter + 1;
      }
    },
    onArrowUp() {
      if (this.arrowCounter > 0) {
        this.arrowCounter = this.arrowCounter - 1;
      }
    },
    onEnter() {
      console.info("enter", this.arrowCounter)
      if (this.arrowCounter != -1) {
        if (this.search.split(" ").length > 1) {
          this.search = this.search.split(" ").slice(0, -1).join(" ")
        }
        // based on the selection from suggestions add the suggested word to 
        this.search = this.search + " " + this.results[this.arrowCounter];
      }
      this.isOpen = false
      this.arrowCounter = -1
    },
    setResult(result) {
      this.search = this.search + " " + result;
      this.isOpen = false;
    },
    handleClickOutside(evt) {
      if (!this.$el.contains(evt.target)) {
        this.isOpen = false;
        this.arrowCounter = -1;
      }
    }
  }
}
</script>

<style>
.autocomplete {
  position: relative;
  width: 130px;
}

.autocomplete-results {
  padding: 0;
  margin: 0;
  border: 1px solid #eeeeee;
  height: 120px;
  overflow: auto;
  width: 100%;
}

.autocomplete-result {
  list-style: none;
  text-align: left;
  padding: 4px 2px;
  cursor: pointer;
}

.autocomplete-result.is-active,
.autocomplete-result:hover {
  background-color: #4aae9b;
  color: white;
}
</style>