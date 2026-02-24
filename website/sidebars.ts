import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quick-start',
      ],
    },
    {
      type: 'category',
      label: 'User Guide',
      items: [
        'guide/configuration',
        'guide/cli-usage',
        'guide/background-service',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/architecture',
        'api/core-modules',
      ],
    },
    {
      type: 'category',
      label: 'Development',
      items: [
        'development/testing',
        'development/contributing',
      ],
    },
    'faq',
    'changelog',
    'code-of-conduct',
  ],
};

export default sidebars;
