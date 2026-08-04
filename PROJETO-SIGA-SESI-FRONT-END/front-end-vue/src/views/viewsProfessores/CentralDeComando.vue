<script setup lang="ts">
import ProfessorDesign from './design.vue'

const indicadores = [
  { titulo: 'Turmas ativas', valor: '12', icon: 'mdi-google-classroom' },
  { titulo: 'Avisos recentes', valor: '08', icon: 'mdi-bell-outline' },
  { titulo: 'Atividades abertas', valor: '05', icon: 'mdi-clipboard-text-outline' },
]
</script>

<template>
  <ProfessorDesign
    title="Central de Controle"
    eyebrow="PAINEL DO PROFESSOR"
    description="Acompanhe as principais informações do professor em um painel único."
    active="central"
  >
    <template #hero-action>
      <div class="hero-stat">
        <v-icon icon="mdi-view-dashboard-outline" size="22" />
        <strong>3</strong>
        <span>indicadores</span>
      </div>
    </template>

    <div class="workspace">
      <section class="panel">
        <div class="section-heading">
          <span>01</span>
          <div>
            <h2>Resumo geral</h2>
            <p>Use este espaço para adicionar os dados principais da central.</p>
          </div>
        </div>

        <div class="command-grid">
          <article v-for="item in indicadores" :key="item.titulo" class="command-card">
            <v-icon :icon="item.icon" size="28" />
            <strong>{{ item.valor }}</strong>
            <span>{{ item.titulo }}</span>
          </article>
        </div>
      </section>

      <aside class="side-column">
        <section class="preview-card">
          <div class="preview-label">
            <span>ATALHO</span>
            <v-chip size="small" color="#c7192d" variant="tonal">Professor</v-chip>
          </div>
          <h3>Notificações</h3>
          <p>
            O botão lateral Notificações leva de volta para a tela principal do professor.
          </p>
        </section>

        <section class="recent-card">
          <div class="recent-heading">
            <div>
              <span>MODELO</span>
              <h2>Próximas áreas</h2>
            </div>
            <v-icon icon="mdi-plus-circle-outline" color="#c7192d" />
          </div>
          <p class="support-text">
            Crie novas páginas em viewsProfessores usando o arquivo design.vue como base visual.
          </p>
        </section>
      </aside>
    </div>
  </ProfessorDesign>
</template>

<style scoped>
.command-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.command-card {
  min-height: 150px;
  padding: 18px;
  display: grid;
  align-content: center;
  gap: 8px;
  background: #f7f5f2;
  border-left: 3px solid #c7192d;
}

.command-card strong {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 34px;
  font-weight: 500;
  line-height: 1;
}

.command-card span,
.support-text,
.preview-card p {
  color: #67615c;
  font-size: 13px;
  line-height: 1.45;
}

.preview-card h3 {
  margin: 18px 0 8px;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 22px;
  font-weight: 500;
}

.support-text {
  margin: 12px 0 0;
}

@media (max-width: 700px) {
  .command-grid {
    grid-template-columns: 1fr;
  }
}
</style>
