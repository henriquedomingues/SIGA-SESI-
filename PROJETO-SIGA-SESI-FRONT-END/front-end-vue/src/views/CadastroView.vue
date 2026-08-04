<script setup>

import { ref } from "vue"

/* CAMPOS */

const name = ref("")
const telefone = ref("")
const cpf = ref("")
const email = ref("")
const password = ref("")


/* ERROS */

const erroNome = ref("")    
const erroTelefone = ref("")
const erroCpf = ref("")
const erroEmail = ref("")
const erroSenha = ref("")


/* VALIDAÇÃO DINAMICA SENHA */

const senhaMaiuscula = ref(false)
const senhaNumero = ref(false)
const senhaTamanho = ref(false)


function validarSenha(){

  senhaMaiuscula.value = /[A-Z]/.test(password.value)
  senhaNumero.value = /\d/.test(password.value)
  senhaTamanho.value = password.value.length >= 6

  if(!senhaMaiuscula.value){
    erroSenha.value = "A senha precisa ter uma letra maiúscula"
    return
  }

  if(!senhaNumero.value){
    erroSenha.value = "A senha precisa ter um número"
    return
  }

  if(!senhaTamanho.value){
    erroSenha.value = "A senha precisa ter no mínimo 6 caracteres"
    return
  }

  erroSenha.value = ""
}

/* Confirmar senha*/

const confirmPassword = ref("")
const erroConfirmSenha = ref("")

function validarConfirmSenha(){



  if(confirmPassword.value !== password.value){
    erroConfirmSenha.value = "As senhas não coincidem"
  }else{
    erroConfirmSenha.value = ""
  }

}


/* MASCARA TELEFONE */

function mascaraTelefone(){

  let v = telefone.value.replace(/\D/g,"")

  if(v.length > 11){
    v = v.slice(0,11)
  }

  v = v.replace(/^(\d{2})(\d)/g,"($1) $2")
  v = v.replace(/(\d{5})(\d)/,"$1-$2")

  telefone.value = v

}


/* MASCARA CPF */

function mascaraCpf(){

  let v = cpf.value.replace(/\D/g,"")

  if(v.length > 11){
    v = v.slice(0,11)
  }

  v = v.replace(/(\d{3})(\d)/,"$1.$2")
  v = v.replace(/(\d{3})(\d)/,"$1.$2")
  v = v.replace(/(\d{3})(\d{1,2})$/,"$1-$2")

  cpf.value = v

}


/* VALIDAR CPF */

function validarCPF(cpfValor){

  let cpf = cpfValor.replace(/\D/g,"")

  if(cpf.length !== 11){
    return false
  }

  if(/^(\d)\1+$/.test(cpf)){
    return false
  }

  let soma = 0

  for(let i=0;i<9;i++){
    soma += parseInt(cpf.charAt(i)) * (10 - i)
  }

  let resto = 11 - (soma % 11)

  if(resto >= 10){
    resto = 0
  }

  if(resto !== parseInt(cpf.charAt(9))){
    return false
  }

  soma = 0

  for(let i=0;i<10;i++){
    soma += parseInt(cpf.charAt(i)) * (11 - i)
  }

  resto = 11 - (soma % 11)

  if(resto >= 10){
    resto = 0
  }

  if(resto !== parseInt(cpf.charAt(10))){
    return false
  }

  return true

}


/* SUBMIT */

function submit(){

  erroNome.value = ""
  erroTelefone.value = ""
  erroCpf.value = ""
  erroEmail.value = ""
  erroSenha.value = ""


  if(name.value.length < 3){
    erroNome.value = "Nome muito curto"
  }


  if(telefone.value.length < 15){
    erroTelefone.value = "Telefone inválido"
  }


  if(!validarCPF(cpf.value)){
    erroCpf.value = "CPF inválido"
  }


  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  if(!emailRegex.test(email.value)){
    erroEmail.value = "Email inválido"
  }


  if(!senhaMaiuscula.value || !senhaNumero.value || !senhaTamanho.value){
    erroSenha.value = "Senha não atende os requisitos"
  }

  if(confirmPassword.value !== password.value){
    erroConfirmSenha.value = "As senhas não coincidem"
    }

}

</script>
    
<template>
   
   <!---Fundo caindo-->>
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

    <form  class="bloco" @submit.prevent="submit">
        
        <div class="container">

            <div class="espaco">

                <label for="name">Nome</label>
                <div class="input">
                <input
                    type="text"
                    id="name"
                    v-model="name"
                    placeholder="Digite seu nome"
                    />
                </div>
                    <small style="color:red">{{erroNome}}</small>
                </div>


                <div class="espaco">
                    <label for="telefone">Telefone</label>

                    <div class="input">
                        <input
                            type="text"
                            id="telefone"
                            v-model="telefone"
                            @input="mascaraTelefone"
                            placeholder="(00) 00000-0000"
                            />
                    </div>

                    <small style="color:red">{{erroTelefone}}</small>

                </div>


                <div class="espaco">

                <label for="cpf">CPF</label>

                <div class="input">
                <input
                type="text"
                id="cpf"
                v-model="cpf"
                @input="mascaraCpf"
                placeholder="000.000.000-00"
                />
                </div>

                <small style="color:red">{{erroCpf}}</small>

                </div>


                <div class="espaco">

                <label for="email">Email</label>

                <div class="input">
                <input
                type="email"
                id="email"
                v-model="email"
                placeholder="Digite seu email"
                />
                </div>

                <small style="color:red">{{erroEmail}}</small>

                </div>


                <div class="espaco">

                    <label for="password">Senha</label>

                    <div class="input">
                        <input
                        type="password"
                        id="password"
                        v-model="password"
                        @input="validarSenha"
                        placeholder="Crie uma senha"
                        />

                           
                </div>

                <small style="color:red">{{erroSenha}}</small>

                </div>

                <div class="espaco">

                <label for="confirmPassword">Confirmar senha</label>

                    <div class="input">
                        <input
                        type="password"
                        id="confirmPassword"
                        v-model="confirmPassword"
                        @input="validarConfirmSenha"
                        placeholder="Digite a senha novamente"
                        />
                    </div>

                    <small style="color:red">{{erroConfirmSenha}}</small>

                </div>
               
                <div class="espaco-botao">
                    <button type="submit">Cadastrar</button>

                </div>

        </div>

    </form>

    

    <!-- 
    <form class="bloco" action="" method="post">
        <div class="container">
            <div class="espaco">
                <div class="input">
                    <input type="text"
                    id="name"
                    name="name"  
                    placeholder="Nome">
                </div>
            </div>

            <div class="espaco">
                <div class="input">
                    <input type="text"
                    id="telefone"
                    name="telefone"
                    placeholder="(00) 00000-0000"
                    pattern="\(\d{2}\)\s\d{5}-\d{4}"
                    required>
                </div>
            </div>

            <div class="espaco">
                <div class="input">
                    <input type="text" 
                    id="cpf"
                    name="cpf"
                    placeholder="Digite seu CPF">
                </div>
            </div>

            <div class="espaco">
                <div class="input">
                    <input type="email" 
                    id="email"
                    name="email"
                    placeholder="Digite seu email">
                </div>
            </div>

            <div class="espaco">
                <div class="input">
                    <input type="password"
                    id="password"
                    name="password"
                     placeholder="Crie uma senha">

                </div>
            </div>


        </div>


    </form>
-->



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




.bloco{
   position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 90%;
  max-width: 800px;
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

.espaco {
    padding-top: 5px;
    padding-bottom: 5   px;
}

.validacaoSenha{
  font-size: 13px;
  margin-top: 5px;
}

label{

  
    font-family: Arial, Helvetica, sans-serif;
    
}

small{
  font-family: Arial, Helvetica, sans-serif;
  
}


.espaco {
  padding-top: 10px;
  padding-bottom: 10px;
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

  display: flex;
  justify-content: flex-end;
  margin-left: auto;

}

.espaco-botao{
  padding-top: 30px;
}

</style>