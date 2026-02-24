import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import styles from './index.module.css';

const techLogos = [
  {
    name: 'Python',
    svg: (
      <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
        <path d="M11.914 0C5.82 0 6.2 2.656 6.2 2.656l.007 2.752h5.814v.826H3.9S0 5.789 0 11.969c0 6.18 3.403 5.96 3.403 5.96h2.03v-2.867s-.109-3.403 3.35-3.403h5.766s3.24.052 3.24-3.134V3.075S18.29 0 11.914 0zM8.708 1.776a1.06 1.06 0 0 1 1.06 1.06 1.06 1.06 0 0 1-1.06 1.06 1.06 1.06 0 0 1-1.06-1.06 1.06 1.06 0 0 1 1.06-1.06z" />
        <path d="M12.086 24c6.094 0 5.714-2.656 5.714-2.656l-.007-2.752h-5.814v-.826h8.123s3.9.445 3.9-5.735c0-6.18-3.403-5.96-3.403-5.96h-2.03v2.867s.109 3.403-3.35 3.403H9.453s-3.24-.052-3.24 3.134v5.45S5.71 24 12.086 24zm3.206-1.776a1.06 1.06 0 0 1-1.06-1.06 1.06 1.06 0 0 1 1.06-1.06 1.06 1.06 0 0 1 1.06 1.06 1.06 1.06 0 0 1-1.06 1.06z" />
      </svg>
    ),
  },
  {
    name: 'Bluetooth',
    svg: (
      <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
        <path d="M12.005 0 7.455 4.55l4.55 4.55-4.55 4.55 4.55 4.55V24l6.545-6.545-4.55-4.55 4.55-4.55L12.005 0zm1 7.39V3.16l2.115 2.115L13.005 7.39zm0 13.45v-4.23l2.115 2.115-2.115 2.115z" />
      </svg>
    ),
  },
  {
    name: 'macOS',
    svg: (
      <svg viewBox="0 0 24 24" fill="currentColor" width="28" height="28">
        <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" />
      </svg>
    ),
  },
];

const features = [
  {
    title: 'BLE Device Discovery',
    emoji: '🔍',
    description: 'Scan and identify nearby Bluetooth Low Energy devices with real-time signal strength and estimated distance.',
  },
  {
    title: 'Automatic Locking',
    emoji: '🔒',
    description: 'Instantly locks your macOS screen when your trusted device moves beyond a configurable distance threshold.',
  },
  {
    title: 'Background Service',
    emoji: '🚀',
    description: 'Run as a persistent daemon with full service lifecycle management — start, stop, restart, and status.',
  },
  {
    title: 'Highly Configurable',
    emoji: '⚙️',
    description: 'Fine-tune distance thresholds, TX power calibration, path loss exponent, and signal smoothing for your environment.',
  },
  {
    title: 'Smart Recovery',
    emoji: '🛡️',
    description: 'Lock loop protection, watchdog monitoring, and automatic scanner reconnection with exponential backoff.',
  },
  {
    title: 'Privacy First',
    emoji: '🔐',
    description: 'Runs 100% locally. No internet, no telemetry, no data collection. Fully open source and auditable.',
  },
];

function Feature({title, emoji, description}: {title: string; emoji: string; description: string}) {
  return (
    <div className={styles.feature}>
      <div className={styles.featureEmoji}>{emoji}</div>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

export default function Home(): React.JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout description={siteConfig.tagline}>
      <header className={styles.hero}>
        <div className={styles.heroInner}>
          <h1 className={styles.heroTitle}>🥐 B.R.I.O.S.</h1>
          <p className={styles.heroSubtitle}>{siteConfig.tagline}</p>
          <p className={styles.heroDescription}>
            A proximity monitoring system for macOS that automatically locks your Mac
            when your iPhone, Apple Watch, or any Bluetooth device moves out of range.
          </p>
          <div className={styles.heroButtons}>
            <Link className="button button--primary button--lg" to="/docs/getting-started/installation">
              Get Started
            </Link>
            <Link className="button button--secondary button--lg" to="/docs/intro">
              Documentation
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className={styles.techStrip}>
          <div className={styles.techLogos}>
            {techLogos.map((logo, idx) => (
              <span key={idx} className={styles.techLogo} title={logo.name}>
                {logo.svg}
                <span>{logo.name}</span>
              </span>
            ))}
          </div>
        </section>

        <section className={styles.features}>
          <div className="container">
            <div className={styles.featuresGrid}>
              {features.map((props, idx) => (
                <Feature key={idx} {...props} />
              ))}
            </div>
          </div>
        </section>

        <section className={styles.quickStart}>
          <div className="container">
            <h2>Quick Start</h2>
            <pre className={styles.codeBlock}>
{`# Install via Homebrew
brew tap Piero24/brios https://github.com/Piero24/B.R.I.O.S.
brew install brios

# Discover nearby devices
brios --scanner 15 -m

# Configure and start monitoring
brios --start`}
            </pre>
          </div>
        </section>
      </main>
    </Layout>
  );
}
