<script setup>
import { ref } from "vue"
import CadastroView from "./CadastroView.vue" 
import axios from "axios"


const emailUser = ref("")
const passwordUser = ref("")

const emailErro = ref("")
const passwordErro = ref("")

async function login(){

  try{

    const response = await axios.post(
      "http://localhost:8081/auth/login",
      {
        email: emailUser.value,
        password: passwordUser.value
      }
    )

    console.log(response.data)

  }catch(error){
    console.log(error)
  }

}


function submit(){

  emailErro.value = ""
  passwordErro.value = ""

  if (!email.value) {
  emailErro.value = "Digite seu email"
  } 
  else if (!email.value.includes("@") || email.value.split("@")[1] === "") {
    emailErro.value = "Email inválido"
  }

  if(!password.value){
    passwordErro.value = "Digite sua senha"
  } 
  else if(password.value.length < 6){
    passwordErro.value = "Mínimo de 6 caracteres"
  }

  if(emailErro.value || passwordErro.value){
    return
  }

  console.log("Login válido")
}
</script>

<template>


    <!---Fundo caindo-->
    <div class="lines">
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    <div class="line"></div>
    </div>

    

  <form @submit.prevent="submit" method="post" class="bloco" novalidate>
   <img src="../images/Logo_SESI_vermelho.jpg" alt="Logo Sesi">

  <div class="container">

    <div class="teste">
      <div class="input"> 
        <input 
          type="text"
          v-model="emailUser"
          placeholder="Digite seu email"
        >
        <font-awesome-icon :icon="['fas', 'user']" class="i"/>
      </div>

      <p v-if="emailErro" class="erro">{{ emailErro }}</p>
    </div>


  
      <div class="input" id="senhaTop">
        <input 
          type="password"
          v-model="passwordUser"
          placeholder="Digite sua senha"
        >
        <font-awesome-icon icon="fa-solid fa-lock" class="i" />
      </div>

        <p v-if="passwordErro" class="erro">{{ passwordErro }}</p>
 
    

    <div class="actions">
      <button type="submit">
        Entrar
      </button>

      <a href="">Esqueceu a senha?</a>

      <router-link class="conta-nova" to="/cadastro">Criar nova conta</router-link>


    
    </div>

  </div>

</form>
  
</template>

<style scoped>
    
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}


html, body {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
}

body {
  display: table;
  width: 100%;
  height: 100%;
  background-color: #0a0a0a;  /* Background color */
  color: #000000;  /* Text color */
  line-height: 1.6;
  position: relative;
  font-family: sans-serif;
  overflow: hidden;
  margin: 0;
    overflow-x: hidden;

}

.lines {

  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  margin: 0;
 
  display: flex;
  justify-content: space-between; /* Distribute lines evenly */
  background-color: #0a0a0aec;  
}

.line {
  position: relative;
  width: 1px;
  height: 100%;
  /*background: #ffffff;  /* Line color */
  overflow: hidden;
  
}

.line::after {
  content: '';
  display: block;
  position: absolute;
  height: 15vh;
  width: 100%;
  top: -50%;
  left: 0;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation: drop 7s 0s infinite;
  animation-fill-mode: forwards;
  animation-timing-function: cubic-bezier(0.4, 0.26, 0, 0.97);
}

/* Different colors for each line's pseudo-element */
.line:nth-child(1)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 0.5s;
}

.line:nth-child(2)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 1s;
}

.line:nth-child(3)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 1.5s;
}

.line:nth-child(4)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 2s;
}

.line:nth-child(5)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 2.5s;
}

.line:nth-child(6)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 3s;
}

.line:nth-child(7)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 3.5s;
}

.line:nth-child(8)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 4s;
}

.line:nth-child(9)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 4.5s;
}

.line:nth-child(10)::after {
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0) 0%, #FF0000 75%, #FF0000 100%);
  animation-delay: 5s;
}

@keyframes drop {
  0% {
    top: -50%;
  }
  100% {
    top: 110%;
  }
}




img {
  padding-bottom: 20px;
}






.erro{
  color: red;
  font-size: 12px;
  margin-top: 2px;
  font-family: Arial, Helvetica, sans-serif;
  padding: 1px 1px 1px 1px;
  padding-top: 3px;
}


#senhaTop{
  margin-top: 10px;
}






.bloco{
   position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 400px;
  z-index: 2;

  
}

.container {
 margin: 0 auto;
  border-radius: 12px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.3);
  background: white;
  padding: 30px;
  width: 100%;
}

h2 {
  margin-bottom: 20px;
  text-align: center;
}

.field {
  margin-bottom: 18px;
  display: flex;
  flex-direction: column;
}

label {
  margin-bottom: 6px;
  font-weight: 600;
}

input {
  padding: 14px;  
  border-radius: 10px;
  border: 1px solid #646262;
  font-size: 16px;
  transition: 0.3s;

  padding-right: 50px;

  width: 100%;
  max-width: 400px;
  height: 40px;

}

input:focus {
  border-color: #485851c2;
  outline: none;
}

.invalid {
  border-color: #e74c3c;
  background-color: #fff6f6;
}

.error {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 5px;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 10px;
  font-family: Arial, Helvetica, sans-serif;
}

button {
  padding: 12px;
  border-radius: 6px;
  border: none;
  background: red;
  color: white;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
}

button:hover {
  background: rgb(147, 3, 3);
}

button:disabled {
  background: #cccccc;

}

.esqueceu-senha {
    color: rgb(1, 120, 232);
}

a {
  
  padding-top: 3px;  
  text-align: center;
  font-size: 14px;
  color: #db3722;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.conta-nova{
  color: #0064E0;
}

h2{
    font-size: 60px;

    color: white;
    font-family: Arial, Helvetica, sans-serif;
    
}

.input{
  background-color: white;
  width: 100%;
  height: 48px;
  position: relative;
  display: flex;
  align-items: center;
  border: 1px solid #ccc;
  border-radius: 8px;
  overflow: hidden;

}

.input input{
 height: 100%;
  width: 100%;
  border: none;
  padding: 0 45px 0 15px;
  font-size: 16px;
  outline: none;
}

.i {
position: absolute;
  right: 15px;
  color: #666;
  pointer-events: none;

}


</style>
