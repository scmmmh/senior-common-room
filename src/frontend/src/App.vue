<template>
    <div id="nav">
        <router-link to="/">Home</router-link> |
        <router-link to="/about">About</router-link>
    </div>
    <router-view/>
</template>

<script lang="ts">
import { Options, Vue } from 'vue-class-component';

@Options({
    components: {
    },
})
export default class App extends Vue {
    async mounted() {
        this.$store.dispatch('init');
    }
}
</script>
