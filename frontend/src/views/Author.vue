<template>
  <section class="page-shell author-page">
    <header class="page-header">
      <div class="page-header__main">
        <h1 class="page-title">关于作者</h1>
        <p class="page-subtitle">全栈工程师、AI 探索者与效率工具实践者。</p>
      </div>
    </header>

    <div class="page-content">
      <section class="section-card author-hero">
        <div class="section-card__body author-hero__body">
          <div class="author-profile">
            <div class="author-avatar">
              <img :src="authorInfo.avatar" :alt="authorInfo.name" />
            </div>
            <div class="author-copy">
              <span class="author-eyebrow">程序员老蔡</span>
              <h2 class="author-name">{{ authorInfo.name }}</h2>
              <p class="author-tagline">{{ authorInfo.tagline }}</p>
              <span class="author-note">10年+ 技术沉淀，持续拥抱变化</span>
            </div>
          </div>

          <div class="author-bio">
            <p>
              从 <strong>Java 后端</strong>起步，逐步延展到前端工程、自动化流程与 AI 集成。
              当前重点是用工具化方式减少内容分发中的重复劳动，让创作者把精力放回内容本身。
            </p>
            <p>
              这套工具是对效率、流程稳定性与产品一致性的持续实践，也是将工程能力转化为业务生产力的一次落地。
            </p>
          </div>
        </div>
      </section>

      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">技术栈与能力</h2>
          <p class="section-subtitle">围绕自动化发布、全栈开发与 AI 集成的长期积累。</p>
        </div>
        <div class="section-card__body">
          <div class="skill-grid">
            <span class="skill-chip" v-for="skill in authorInfo.skills" :key="skill">{{ skill }}</span>
          </div>
        </div>
      </section>

      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">项目与链接</h2>
          <p class="section-subtitle">公开项目、个人站点与 AI 产品探索。</p>
        </div>
        <div class="section-card__body project-grid">
          <a class="project-card" v-for="project in authorInfo.projects" :key="project.name" :href="project.url" target="_blank" rel="noopener">
            <span class="project-card__icon" :style="{ background: project.gradient }">
              <component :is="project.icon" />
            </span>
            <strong class="project-card__title">{{ project.name }}</strong>
            <span class="project-card__desc">{{ project.desc }}</span>
            <span class="project-card__link">{{ project.url.replace('https://', '') }}</span>
          </a>
        </div>
      </section>

      <section class="section-card">
        <div class="section-card__header">
          <h2 class="section-title">联系方式</h2>
        </div>
        <div class="section-card__body contact-panel">
          <div class="qr-card">
            <div class="qr-card__thumb">
              <img :src="authorInfo.wechatQr" alt="微信二维码" />
              <div class="qr-card__zoom">
                <img :src="authorInfo.bigQrcode" alt="微信二维码" />
              </div>
            </div>
            <span class="qr-card__label">微信扫码联系</span>
          </div>

          <div class="contact-copy">
            <h3>让我们连接</h3>
            <p>无论是技术交流还是项目合作，都可以通过微信或 GitHub 联系。</p>
          </div>

          <a class="contact-link" href="https://github.com/DevilJie" target="_blank" rel="noopener">
            <component :is="GithubIcon" />
            GitHub
          </a>
        </div>
      </section>
    </div>
  </section>
</template>

<script setup>
import { h } from 'vue'
import headImg from '@/assets/head.png'
import qrcodeImg from '@/assets/qrcode.png'
import bigQrcodeImg from '@/assets/big_qrcode.jpg'

const BlogIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M12 20h9M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z' }),
    ])
  },
}

const AiIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
      h('path', { d: 'M12 2a10 10 0 1 0 10 10H12V2zM12 2a10 10 0 0 1 10 10' }),
    ])
  },
}

const GithubIcon = {
  render() {
    return h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
      h('path', { d: 'M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z' }),
    ])
  },
}

const authorInfo = {
  name: '程序员老蔡',
  avatar: headImg,
  tagline: '全栈工程师 · AI 探索者 · 效率工具研究者',
  skills: ['Java', 'Spring Boot', 'Vue.js', 'React', 'Python', 'Flask', 'Playwright', 'AI 集成', '自动化'],
  wechatQr: qrcodeImg,
  bigQrcode: bigQrcodeImg,
  projects: [
    {
      name: '个人博客',
      desc: '技术分享、踩坑记录与成长思考',
      url: 'https://blog.cjxch.com',
      icon: BlogIcon,
      gradient: 'linear-gradient(135deg, #14937c, #73d1bb)',
    },
    {
      name: 'AI 创作工厂',
      desc: '一站式 AI 内容创作平台',
      url: 'https://ai.cjxch.com',
      icon: AiIcon,
      gradient: 'linear-gradient(135deg, #2f80ed, #14937c)',
    },
    {
      name: 'GitHub',
      desc: '开源项目与代码实践',
      url: 'https://github.com/DevilJie',
      icon: GithubIcon,
      gradient: 'linear-gradient(135deg, #394542, #667572)',
    },
  ],
}
</script>

<style lang="scss" scoped>
@use '@/styles/variables.scss' as *;

.author-page {
  .author-hero {
    background: linear-gradient(135deg, rgba($brand-start, 0.08), rgba($info-color, 0.04));
    border-color: $border-active;
  }

  .author-hero__body {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: $spacing-xl;
    align-items: center;
  }

  .author-profile {
    display: flex;
    align-items: center;
    gap: $spacing-lg;
  }

  .author-avatar {
    width: 120px;
    height: 120px;
    border-radius: 28px;
    overflow: hidden;
    border: 1px solid rgba($brand-start, 0.2);
    box-shadow: $shadow-sm;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }

  .author-copy {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
  }

  .author-eyebrow {
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: $brand-start;
  }

  .author-name {
    font-size: 30px;
    color: $text-primary;
  }

  .author-tagline {
    font-size: 15px;
    color: $text-secondary;
  }

  .author-note {
    display: inline-flex;
    width: fit-content;
    min-height: 28px;
    align-items: center;
    padding: 0 12px;
    border-radius: 999px;
    background: rgba($brand-start, 0.1);
    color: $brand-start;
    font-size: 12px;
    font-weight: 600;
  }

  .author-bio {
    display: flex;
    flex-direction: column;
    gap: $spacing-md;
    color: $text-secondary;
    line-height: 1.8;

    strong {
      color: $text-primary;
    }
  }

  .skill-grid {
    display: flex;
    flex-wrap: wrap;
    gap: $spacing-sm;
  }

  .skill-chip {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 0 12px;
    border-radius: 999px;
    background: $bg-surface;
    border: 1px solid $border;
    color: $text-secondary;
    font-size: 12px;
    font-weight: 600;
  }

  .project-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: $spacing-lg;
  }

  .project-card {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
    padding: $spacing-lg;
    border-radius: $radius-card;
    border: 1px solid $border;
    background: $bg-elevated;
    transition:
      transform $transition-base,
      border-color $transition-base,
      box-shadow $transition-base;

    &:hover {
      transform: translateY(-2px);
      border-color: $border-active;
      box-shadow: $shadow-md;
    }
  }

  .project-card__icon {
    width: 48px;
    height: 48px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: $radius-base;
    color: #fff;

    :deep(svg) {
      width: 22px;
      height: 22px;
    }
  }

  .project-card__title {
    font-size: 16px;
    color: $text-primary;
  }

  .project-card__desc {
    font-size: 13px;
    color: $text-secondary;
    line-height: 1.7;
  }

  .project-card__link {
    font-size: 12px;
    color: $brand-start;
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }

  .contact-panel {
    display: grid;
    grid-template-columns: 180px minmax(0, 1fr) 180px;
    gap: $spacing-xl;
    align-items: center;
  }

  .qr-card {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: $spacing-sm;
  }

  .qr-card__thumb {
    position: relative;
    width: 104px;
    height: 104px;
    padding: 8px;
    border-radius: $radius-base;
    background: #fff;
    box-shadow: $shadow-sm;

    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    &:hover .qr-card__zoom {
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }
  }

  .qr-card__zoom {
    position: absolute;
    left: 120px;
    top: -16px;
    width: 200px;
    padding: 8px;
    border-radius: $radius-card;
    background: #fff;
    box-shadow: $shadow-lg;
    opacity: 0;
    transform: translateY(6px);
    pointer-events: none;
    transition: opacity $transition-base, transform $transition-base;
    z-index: 3;

    img {
      width: 100%;
      height: auto;
    }
  }

  .qr-card__label {
    font-size: 12px;
    color: $text-secondary;
  }

  .contact-copy {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;

    h3 {
      font-size: 20px;
      color: $text-primary;
    }

    p {
      color: $text-secondary;
      line-height: 1.7;
    }
  }

  .contact-link {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 42px;
    padding: 0 18px;
    border-radius: $radius-base;
    border: 1px solid $border;
    background: $bg-elevated;
    color: $text-primary;
    font-weight: 600;

    :deep(svg) {
      width: 18px;
      height: 18px;
    }
  }

  @media (max-width: 1024px) {
    .author-hero__body,
    .contact-panel,
    .project-grid {
      grid-template-columns: 1fr;
    }

    .author-profile {
      flex-direction: column;
      align-items: flex-start;
    }

    .qr-card__zoom {
      left: 0;
      top: 120px;
    }
  }
}
</style>
