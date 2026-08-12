/* ================================================================
   MAIN.JS — Navigation, typewriter, RELIABLE reveal system
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Navbar scroll ─────────────────────────────────────────────
  const navbar = document.getElementById('navbar');
  function handleScroll() {
    if (navbar) navbar.classList.toggle('scrolled', window.scrollY > 20);
    updateActiveNavLink();
  }
  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // ── Active nav link on scroll ─────────────────────────────────
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link[data-section]');

  function updateActiveNavLink() {
    let current = '';
    sections.forEach(sec => {
      if (window.scrollY >= sec.offsetTop - 100) current = sec.getAttribute('id');
    });
    navLinks.forEach(link => {
      link.classList.toggle('active', link.dataset.section === current);
    });
  }

  // ── Smooth scroll ─────────────────────────────────────────────
  const hamburger = document.getElementById('hamburger');
  const mobileNav = document.getElementById('mobile-nav');

  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const href = anchor.getAttribute('href');
      if (href === '#') return;
      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        if (hamburger) hamburger.classList.remove('open');
        if (mobileNav) mobileNav.classList.remove('open');
      }
    });
  });

  // ── Mobile hamburger ──────────────────────────────────────────
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      mobileNav.classList.toggle('open');
    });
    document.addEventListener('click', e => {
      if (mobileNav.classList.contains('open') &&
          !mobileNav.contains(e.target) &&
          !hamburger.contains(e.target)) {
        hamburger.classList.remove('open');
        mobileNav.classList.remove('open');
      }
    });
  }

  // ── Typewriter effect ─────────────────────────────────────────
  const typedTarget = document.getElementById('typed-text');
  if (typedTarget) {
    const phrases = [
      'AI & Data Science Student',
      'Aspiring Full-Stack Developer',
      'Machine Learning Enthusiast',
      'Problem Solver'
    ];
    let phraseIndex = 0, charIndex = 0, isDeleting = false, speed = 80;

    function type() {
      const phrase = phrases[phraseIndex];
      typedTarget.textContent = isDeleting
        ? phrase.substring(0, --charIndex)
        : phrase.substring(0, ++charIndex);

      speed = isDeleting ? 45 : 80;

      if (!isDeleting && charIndex === phrase.length) {
        speed = 2200; isDeleting = true;
      } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        phraseIndex = (phraseIndex + 1) % phrases.length;
        speed = 400;
      }
      setTimeout(type, speed);
    }
    setTimeout(type, 1200);
  }

  // ── RELIABLE REVEAL SYSTEM ─────────────────────────────────────
  // Strategy:
  //   1. Immediately reveal elements already visible in viewport
  //   2. Use IntersectionObserver (threshold=0) for the rest
  //   3. Safety net: force-reveal everything after 1.5s

  function revealEl(el) {
    el.classList.add('revealed');
  }

  function setupRevealObserver() {
    const allReveal = document.querySelectorAll('.reveal:not(.revealed)');
    if (allReveal.length === 0) return;

    // Step 1: Immediately reveal anything already in view
    allReveal.forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.top < window.innerHeight + 100 && r.bottom > 0) {
        revealEl(el);
      }
    });

    // Step 2: Observe the rest with a very permissive observer
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          revealEl(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0,
      rootMargin: '0px 0px 80px 0px'   // trigger 80px BEFORE element enters view
    });

    document.querySelectorAll('.reveal:not(.revealed)').forEach(el => observer.observe(el));

    // Step 3: Safety net — force reveal everything still hidden after 1.5s
    setTimeout(() => {
      document.querySelectorAll('.reveal:not(.revealed)').forEach(el => revealEl(el));
    }, 1500);
  }

  setupRevealObserver();

  // Export so projects.js can call after dynamic load
  window.setupRevealObserver = setupRevealObserver;

  // ── Scroll-triggered re-check ─────────────────────────────────
  // Also reveal on scroll as a belt-and-suspenders approach
  let ticking = false;
  window.addEventListener('scroll', () => {
    if (!ticking) {
      requestAnimationFrame(() => {
        document.querySelectorAll('.reveal:not(.revealed)').forEach(el => {
          const r = el.getBoundingClientRect();
          if (r.top < window.innerHeight - 20 && r.bottom > 0) revealEl(el);
        });
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  // ── Animated stat counters ────────────────────────────────────
  const statNums = document.querySelectorAll('.stat-number[data-target]');
  if (statNums.length > 0) {
    const counterObs = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0 });
    statNums.forEach(el => counterObs.observe(el));
  }

  function animateCounter(el) {
    const target = parseFloat(el.dataset.target);
    const isDecimal = String(target).includes('.');
    const duration = 1400;
    const start = performance.now();

    function tick(now) {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = (isDecimal ? (target * eased).toFixed(2) : Math.floor(target * eased));
      if (progress < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

});
