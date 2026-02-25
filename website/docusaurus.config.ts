import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: '🥐 B.R.I.O.S.',
  tagline: 'Bluetooth Reactive Intelligent Operator for Croissant Safety',
  favicon: 'img/favicon.svg',

  future: {
    v4: true,
  },

  url: 'https://piero24.github.io',
  baseUrl: '/B.R.I.O.S./',

  organizationName: 'Piero24',
  projectName: 'B.R.I.O.S.',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          editUrl:
            'https://github.com/Piero24/B.R.I.O.S./tree/main/website/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // image: 'img/brios-social-card.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: '🥐 B.R.I.O.S.',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://github.com/Piero24/B.R.I.O.S.',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Documentation',
          items: [
            {
              label: 'Getting Started',
              to: '/docs/getting-started/installation',
            },
            {
              label: 'Configuration',
              to: '/docs/guide/configuration',
            },
            {
              label: 'API Reference',
              to: '/docs/api/architecture',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Issues',
              href: 'https://github.com/Piero24/B.R.I.O.S./issues',
            },
            {
              label: 'GitHub Discussions',
              href: 'https://github.com/Piero24/B.R.I.O.S./discussions',
            },
          ],
        },
        {
          title: 'More',
          items: [
            {
              label: 'Changelog',
              to: '/docs/changelog',
            },
            {
              label: 'GitHub',
              href: 'https://github.com/Piero24/B.R.I.O.S.',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Andrea Pietrobon. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'yaml', 'toml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
