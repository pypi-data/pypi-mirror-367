import { defineConfig } from 'vitepress'
// import { en } from './en'
import { zh } from './zh'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: '/SpectrumLab/',

  // 清理 URL 中的 .html 后缀
  cleanUrls: true,

  // 全局共享配置
  themeConfig: {
    socialLinks: [
      { icon: 'github', link: 'https://github.com/little1d/spectrumlab' }
    ],

    lastUpdated: {
      text: "最后更新于",
      formatOptions: {
        dateStyle: 'full',
        timeStyle: 'medium',
      },
    },

    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: '搜索文档',
                buttonAriaLabel: '搜索文档',
              },
              modal: {
                noResultsText: '无法找到相关结果',
                resetButtonTitle: '清除查询条件',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '关闭',
                }
              }
            }
          },
          // en: {
          //   translations: {
          //     button: {
          //       buttonText: 'Search',
          //       buttonAriaLabel: 'Search',
          //     },
          //     modal: {
          //       noResultsText: 'No results found',
          //       resetButtonTitle: 'Clear search criteria',
          //       footer: {
          //         selectText: 'to select',
          //         navigateText: 'to navigate',
          //         closeText: 'to close',
          //       }
          //     }
          //   }
          // }
        }
      }
    },
  },

  markdown: {
    image: {
      lazyLoading: true,
    }
  },

  // 国际化配置
  locales: {
    root: { label: '简体中文', ...zh },
    // en: { label: 'English', ...en },
  },
})
