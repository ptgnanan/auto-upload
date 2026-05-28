<template>
  <section class="page-shell about-page">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">关于项目</h1>
        <p class="page-subtitle">社交媒体自动上传工具的定位、能力与技术基础。</p>
      </div>
    </header>

    <div class="page-content">
      <section class="section-card about-hero">
        <div class="section-card__body about-hero__body">
          <div class="about-hero__copy">
            <span class="about-badge">social-auto-upload</span>
            <h2 class="about-hero__title">统一管理账号、素材与多平台发布流程</h2>
            <p class="about-hero__text">
              面向内容创作者与运营团队，聚焦账号管理、素材管理、一键发布、定时发布与批量任务跟踪。
            </p>
          </div>
          <div class="about-hero__stats">
            <div class="about-stat">
              <strong>多平台</strong>
              <span>账号接入与统一发布</span>
            </div>
            <div class="about-stat">
              <strong>工作台</strong>
              <span>草稿、素材、配置集中处理</span>
            </div>
            <div class="about-stat">
              <strong>自动化</strong>
              <span>降低重复发布与切换成本</span>
            </div>
          </div>
        </div>
      </section>

      <div class="about-grid">
        <section class="section-card">
          <div class="section-card__header">
            <h2 class="section-title">支持平台</h2>
          </div>
          <div class="section-card__body chip-grid">
            <span class="info-chip info-chip--danger">抖音</span>
            <span class="info-chip info-chip--warning">快手</span>
            <span class="info-chip info-chip--info">视频号</span>
            <span class="info-chip info-chip--primary">小红书</span>
            <span class="info-chip info-chip--info">B站</span>
            <span class="info-chip info-chip--danger">YouTube</span>
          </div>
        </section>

        <section class="section-card">
          <div class="section-card__header">
            <h2 class="section-title">核心功能</h2>
          </div>
          <div class="section-card__body">
            <ul class="feature-list">
              <li>多平台账号管理与登录状态维护</li>
              <li>视频素材上传、预览与素材库复用</li>
              <li>一键多平台发布与差异化字段配置</li>
              <li>定时发布、批量发布与任务状态追踪</li>
              <li>Cookie 导入导出与创作中心联动</li>
            </ul>
          </div>
        </section>
      </div>

      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">技术栈</h2>
        </div>
        <div class="section-card__body chip-grid">
          <span class="tech-chip">Vue 3</span>
          <span class="tech-chip">Element Plus</span>
          <span class="tech-chip">Pinia</span>
          <span class="tech-chip">Flask</span>
          <span class="tech-chip">Playwright</span>
          <span class="tech-chip">SQLite</span>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.about-page {
  .about-hero {
    background: linear-gradient(135deg, rgba($brand-start, 0.08), rgba($brand-end, 0.03));
    border-color: $border-active;
  }

  .about-hero__body {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
    gap: $spacing-xl;
    align-items: center;
  }

  .about-badge {
    display: inline-flex;
    min-height: 28px;
    align-items: center;
    padding: 0 12px;
    border-radius: 999px;
    background: rgba($brand-start, 0.1);
    color: $brand-start;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }

  .about-hero__copy {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .about-hero__title {
    font-size: 30px;
    line-height: 1.2;
    color: $text-primary;
  }

  .about-hero__text {
    font-size: 15px;
    line-height: 1.8;
    color: $text-secondary;
  }

  .about-hero__stats {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
  }

  .about-stat {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: $spacing-md;
    border-radius: $radius-card;
    background: rgba(255, 255, 255, 0.72);
    border: 1px solid $border;

    strong {
      color: $text-primary;
    }

    span {
      color: $text-secondary;
      font-size: 13px;
    }
  }

  .about-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: $spacing-lg;
  }

  .chip-grid {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
  }

  .info-chip,
  .tech-chip {
    display: inline-flex;
    align-items: center;
    min-height: 28px;
    padding: 0 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
  }

  .info-chip--primary {
    background: rgba($brand-start, 0.12);
    color: $brand-start;
  }

  .info-chip--info {
    background: rgba($info-color, 0.12);
    color: $info-color;
  }

  .info-chip--warning {
    background: rgba($warning-color, 0.12);
    color: $warning-color;
  }

  .info-chip--danger {
    background: rgba($danger-color, 0.12);
    color: $danger-color;
  }

  .tech-chip {
    background: $bg-surface;
    color: $text-secondary;
    border: 1px solid $border;
  }

  .feature-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
    color: $text-secondary;
    line-height: 1.7;

    li {
      position: relative;
      padding-left: 16px;

      &::before {
        content: '';
        position: absolute;
        left: 0;
        top: 10px;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: $brand-start;
      }
    }
  }

  @media (max-width: 1024px) {
    .about-hero__body,
    .about-grid {
      grid-template-columns: 1fr;
    }
  }
}
</style>
