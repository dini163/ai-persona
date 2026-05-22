/**
 * AI Persona Hub — Application Logic
 * Search, filter, modal, clipboard, scroll animations
 */

(function () {
  'use strict';

  /* ==================== State ==================== */
  let allCharacters = [];
  let filteredCharacters = [];
  let activeCategory = 'all';
  let searchQuery = '';
  let sources = {};

  /* ==================== DOM Refs ==================== */
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  const grid = $('#gallery-grid');
  const searchInput = $('#search-input');
  const filterContainer = $('#filter-chips');
  const modalOverlay = $('#modal-overlay');
  const statTotal = $('#stat-total');
  const statSources = $('#stat-sources');
  const statCategories = $('#stat-categories');

  /* ==================== Data Loading ==================== */
  async function loadData() {
    try {
      const res = await fetch('data/characters.json');
      const data = await res.json();
      allCharacters = data.characters;
      sources = {};
      data.meta.sources.forEach(s => { sources[s.id] = s; });
      updateStats(data);
      buildFilterChips();
      adjustVisibleChips();
      applyFilters();
    } catch (err) {
      console.error('Failed to load character data:', err);
      grid.innerHTML = `
        <div class="gallery__empty">
          <div class="gallery__empty-icon">⚠️</div>
          <div class="gallery__empty-text">Failed to load characters. Please try refreshing.</div>
        </div>`;
    }
  }

  function updateStats(data) {
    statTotal.textContent = data.characters.length;
    statSources.textContent = data.meta.sources.length;
    const cats = new Set(data.characters.map(c => c.category));
    statCategories.textContent = cats.size;
  }

  /* ==================== Filter Chips ==================== */
  let chipWidths = null;
  let moreBtnWidth = 0;

  function measureChipWidths() {
    if (chipWidths) return;
    
    chipWidths = {};
    const chips = $$('.filter-chip:not(.filter-chip--more)', filterContainer);
    const dropdown = $('#filter-dropdown', filterContainer);
    
    // Save current display states
    const originalDisplays = chips.map(c => ({ el: c, display: c.style.display }));
    const originalDropdownDisplay = dropdown ? dropdown.style.display : '';
    
    // Force visible for measurement
    chips.forEach(c => { c.style.display = 'inline-flex'; });
    if (dropdown) dropdown.style.display = 'inline-block';
    
    // Measure
    chips.forEach(c => {
      chipWidths[c.dataset.cat] = c.offsetWidth;
    });
    if (dropdown) {
      moreBtnWidth = dropdown.offsetWidth;
    }
    
    // Restore display states
    originalDisplays.forEach(item => { item.el.style.display = item.display; });
    if (dropdown) dropdown.style.display = originalDropdownDisplay;
  }

  function adjustVisibleChips() {
    if (!allCharacters.length) return;
    
    measureChipWidths();
    if (!chipWidths) return;
    
    const toolbarInner = $('.toolbar__inner');
    const searchBox = $('.search-box');
    if (!toolbarInner) return;
    
    const isMobile = window.innerWidth <= 768;
    let availableWidth = isMobile 
      ? toolbarInner.clientWidth 
      : (toolbarInner.clientWidth - (searchBox ? searchBox.offsetWidth : 0) - 24);
    
    if (availableWidth <= 0) availableWidth = toolbarInner.clientWidth || 300;
    
    const chips = $$('.filter-chip:not(.filter-chip--more)', filterContainer);
    const otherChips = chips.filter(c => c.dataset.cat !== 'all');
    
    const allChipWidth = chipWidths['all'] || 0;
    const gap = 8;
    
    // Calculate total width if ALL chips were visible
    let totalWidthWithAll = allChipWidth;
    otherChips.forEach(c => {
      totalWidthWithAll += gap + (chipWidths[c.dataset.cat] || 0);
    });
    
    const dropdownContainer = $('#filter-dropdown', filterContainer);
    const dropdownMenu = $('#filter-dropdown-menu', filterContainer);
    const dropdownBtn = $('#more-chips-btn', filterContainer);
    
    let showDropdown = false;
    let visibleCats = new Set(['all']);
    
    if (totalWidthWithAll <= availableWidth) {
      // All chips fit!
      otherChips.forEach(c => visibleCats.add(c.dataset.cat));
      showDropdown = false;
    } else {
      // Need dropdown
      showDropdown = true;
      let currentWidth = allChipWidth;
      const spaceForChips = availableWidth - gap - moreBtnWidth;
      
      for (let i = 0; i < otherChips.length; i++) {
        const c = otherChips[i];
        const cat = c.dataset.cat;
        const w = chipWidths[cat] || 0;
        
        if (currentWidth + gap + w <= spaceForChips) {
          currentWidth += gap + w;
          visibleCats.add(cat);
        } else {
          break;
        }
      }
    }
    
    // Toggle visibility of main chips
    chips.forEach(c => {
      const cat = c.dataset.cat;
      c.style.display = visibleCats.has(cat) ? 'inline-flex' : 'none';
    });
    
    // Toggle visibility of dropdown container
    if (dropdownContainer) {
      dropdownContainer.style.display = showDropdown ? 'inline-block' : 'none';
    }
    
    // Populate and update dropdown menu items
    if (dropdownMenu) {
      const dropdownItems = $$('.filter-dropdown-item', dropdownMenu);
      dropdownItems.forEach(item => {
        const cat = item.dataset.cat;
        if (visibleCats.has(cat)) {
          item.style.display = 'none';
          item.classList.remove('active');
        } else {
          item.style.display = 'flex';
          if (cat === activeCategory) {
            item.classList.add('active');
          } else {
            item.classList.remove('active');
          }
        }
      });
    }
    
    // Update dropdown button text & highlights
    if (dropdownBtn) {
      const isHiddenActive = activeCategory !== 'all' && !visibleCats.has(activeCategory);
      if (isHiddenActive) {
        dropdownBtn.classList.add('active');
        const textSpan = $('.more-chips-text', dropdownBtn);
        if (textSpan) textSpan.textContent = `More: ${activeCategory}`;
        
        // Remove active class from all main row chips
        chips.forEach(c => c.classList.remove('active'));
      } else {
        dropdownBtn.classList.remove('active');
        const textSpan = $('.more-chips-text', dropdownBtn);
        if (textSpan) textSpan.textContent = 'More';
        
        // Highlight active main chip
        chips.forEach(c => {
          c.classList.toggle('active', c.dataset.cat === activeCategory);
        });
      }
    }
  }

  function buildFilterChips() {
    const categories = {};
    allCharacters.forEach(c => {
      categories[c.category] = (categories[c.category] || 0) + 1;
    });

    const sortedCats = Object.keys(categories).map(cat => ({
      name: cat,
      count: categories[cat]
    })).sort((a, b) => b.count - a.count);

    let html = `<button class="filter-chip active" data-cat="all">All<span class="filter-chip__count">${allCharacters.length}</span></button>`;
    sortedCats.forEach(cat => {
      html += `<button class="filter-chip" data-cat="${cat.name}">${cat.name}<span class="filter-chip__count">${cat.count}</span></button>`;
    });

    html += `
      <div class="filter-dropdown" id="filter-dropdown">
        <button class="filter-chip filter-chip--more" id="more-chips-btn" aria-haspopup="true" aria-expanded="false">
          <span class="more-chips-text">More</span> <span class="more-chips-arrow">▾</span>
        </button>
        <div class="filter-dropdown-menu" id="filter-dropdown-menu" role="menu">
          ${sortedCats.map(cat => `
            <button class="filter-dropdown-item" data-cat="${cat.name}" role="menuitem">
              ${cat.name} <span class="filter-dropdown-item__count">${cat.count}</span>
            </button>
          `).join('')}
        </div>
      </div>
    `;

    filterContainer.innerHTML = html;

    const dropdownBtn = $('#more-chips-btn', filterContainer);
    const dropdownMenu = $('#filter-dropdown-menu', filterContainer);

    if (dropdownBtn && dropdownMenu) {
      dropdownBtn.addEventListener('click', e => {
        e.stopPropagation();
        const isOpen = dropdownMenu.classList.contains('open');
        dropdownMenu.classList.toggle('open', !isOpen);
        dropdownBtn.setAttribute('aria-expanded', !isOpen);
      });

      const dropdownItems = $$('.filter-dropdown-item', dropdownMenu);
      dropdownItems.forEach(item => {
        item.addEventListener('click', e => {
          e.stopPropagation();
          const cat = item.dataset.cat;
          activeCategory = cat;
          dropdownMenu.classList.remove('open');
          dropdownBtn.setAttribute('aria-expanded', 'false');
          
          applyFilters();
          adjustVisibleChips();
        });
      });
    }

    filterContainer.addEventListener('click', e => {
      const chip = e.target.closest('.filter-chip:not(.filter-chip--more)');
      if (!chip) return;

      if (dropdownMenu) {
        dropdownMenu.classList.remove('open');
        dropdownBtn.setAttribute('aria-expanded', 'false');
      }

      activeCategory = chip.dataset.cat;
      applyFilters();
      adjustVisibleChips();
    });

    document.addEventListener('click', () => {
      if (dropdownMenu) {
        dropdownMenu.classList.remove('open');
        dropdownBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ==================== Search ==================== */
  searchInput.addEventListener('input', e => {
    searchQuery = e.target.value.trim().toLowerCase();
    applyFilters();
  });

  /* ==================== Apply Filters ==================== */
  function applyFilters() {
    filteredCharacters = allCharacters.filter(c => {
      const catMatch = activeCategory === 'all' || c.category === activeCategory;
      if (!catMatch) return false;
      if (!searchQuery) return true;
      const haystack = [c.name, c.description, ...c.tags, c.category, c.source].join(' ').toLowerCase();
      return haystack.includes(searchQuery);
    });
    renderCards();
  }

  /* ==================== Render Cards ==================== */
  function renderCards() {
    if (filteredCharacters.length === 0) {
      grid.innerHTML = `
        <div class="gallery__empty">
          <div class="gallery__empty-icon">🔍</div>
          <div class="gallery__empty-text">No characters found. Try a different search or filter.</div>
        </div>`;
      return;
    }

    grid.innerHTML = filteredCharacters.map((c, i) => {
      const source = sources[c.source] || {};
      const catClass = 'cat-' + c.category.toLowerCase().replace(/\s+/g, '-');
      const delay = Math.min(i * 50, 300); // capped at 300ms for high-end snappy feel

      return `
        <article class="card" data-id="${c.id}" style="transition-delay: ${delay}ms" tabindex="0" role="button" aria-label="View ${c.name} prompt">
          <div class="card__header">
            <div class="card__avatar card__avatar--gradient">${c.emoji}</div>
            <div class="card__meta">
              <h3 class="card__name">${c.name}</h3>
              <span class="card__source">
                <span class="card__source-dot" style="background:${source.color || '#666'}"></span>
                ${source.name || c.source}
              </span>
            </div>
          </div>
          <p class="card__desc">${c.description}</p>
          <div class="card__footer">
            <div class="card__tags">
              ${c.tags.slice(0, 2).map(t => `<span class="card__tag">${t}</span>`).join('')}
            </div>
            <span class="card__category-badge ${catClass}">${c.category}</span>
          </div>
        </article>`;
    }).join('');

    // Animate in
    requestAnimationFrame(() => {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

      $$('.card', grid).forEach(card => observer.observe(card));
    });

    // Card mouse tracking for glow
    $$('.card', grid).forEach(card => {
      card.addEventListener('mousemove', e => {
        const rect = card.getBoundingClientRect();
        card.style.setProperty('--mouse-x', ((e.clientX - rect.left) / rect.width * 100) + '%');
        card.style.setProperty('--mouse-y', ((e.clientY - rect.top) / rect.height * 100) + '%');
      });
    });
  }

  /* ==================== Card Click → Modal ==================== */
  grid.addEventListener('click', e => {
    const card = e.target.closest('.card');
    if (!card) return;
    const char = allCharacters.find(c => c.id === card.dataset.id);
    if (char) openModal(char);
  });

  grid.addEventListener('keydown', e => {
    if (e.key === 'Enter') {
      const card = e.target.closest('.card');
      if (!card) return;
      const char = allCharacters.find(c => c.id === card.dataset.id);
      if (char) openModal(char);
    }
  });

  /* ==================== Modal ==================== */
  function openModal(c) {
    const source = sources[c.source] || {};
    const catClass = 'cat-' + c.category.toLowerCase().replace(/\s+/g, '-');

    const modal = $('.modal', modalOverlay);
    modal.innerHTML = `
      <div class="modal__header">
        <div class="modal__avatar">${c.emoji}</div>
        <div class="modal__info">
          <h2 class="modal__name">${c.name}</h2>
          <div class="modal__meta-row">
            <span class="card__category-badge ${catClass}">${c.category}</span>
            <span class="card__source">
              <span class="card__source-dot" style="background:${source.color || '#666'}"></span>
              ${source.name || c.source}
            </span>
          </div>
          <p style="font-size:0.88rem;color:var(--text-secondary);margin-top:4px">${c.description}</p>
        </div>
        <button class="modal__close" id="modal-close" aria-label="Close">✕</button>
      </div>
      <div class="modal__body">
        <h4 class="modal__section-title">System Prompt</h4>
        <div class="modal__prompt-box" id="prompt-text">${escapeHtml(c.prompt)}</div>
        <button class="modal__copy-btn" id="copy-btn">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          Copy Prompt
        </button>

        <h4 class="modal__section-title">Tags</h4>
        <div class="modal__tags">
          ${c.tags.map(t => `<span class="card__tag">${t}</span>`).join('')}
        </div>

        <h4 class="modal__section-title">Compatible With</h4>
        <div class="modal__compat">
          ${c.compatible.map(tool => `<span class="modal__compat-badge">${formatToolName(tool)}</span>`).join('')}
        </div>

        ${source.url ? `
        <h4 class="modal__section-title">Source</h4>
        <a class="modal__source-link" href="${source.url}" target="_blank" rel="noopener">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          ${source.name} on GitHub
        </a>` : ''}
      </div>`;

    modalOverlay.classList.add('open');
    document.body.style.overflow = 'hidden';

    // Copy
    $('#copy-btn', modal).addEventListener('click', () => {
      navigator.clipboard.writeText(c.prompt).then(() => {
        const btn = $('#copy-btn', modal);
        btn.classList.add('copied');
        btn.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
          Copied!`;
        setTimeout(() => {
          btn.classList.remove('copied');
          btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
            Copy Prompt`;
        }, 2000);
      });
    });

    // Close
    $('#modal-close', modal).addEventListener('click', closeModal);

    // Hash
    history.pushState(null, '', '#' + c.id);
  }

  function closeModal() {
    modalOverlay.classList.remove('open');
    document.body.style.overflow = '';
    history.pushState(null, '', window.location.pathname);
  }

  modalOverlay.addEventListener('click', e => {
    if (e.target === modalOverlay) closeModal();
  });

  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && modalOverlay.classList.contains('open')) {
      closeModal();
    }
  });

  /* ==================== URL Hash Routing ==================== */
  function checkHash() {
    const hash = window.location.hash.slice(1);
    if (hash && allCharacters.length) {
      const char = allCharacters.find(c => c.id === hash);
      if (char) openModal(char);
    }
  }

  window.addEventListener('hashchange', checkHash);

  /* ==================== Toolbar Scroll Shadow ==================== */
  const toolbar = $('.toolbar');
  window.addEventListener('scroll', () => {
    toolbar.classList.toggle('scrolled', window.scrollY > 60);
  }, { passive: true });

  /* ==================== Window Resize Listener ==================== */
  window.addEventListener('resize', adjustVisibleChips);

  /* ==================== Helpers ==================== */
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  function formatToolName(tool) {
    const names = {
      openclaw: 'OpenClaw',
      hermes: 'Hermes Agent',
      claude: 'Claude',
      chatgpt: 'ChatGPT',
      manual: 'Manual Use'
    };
    return names[tool] || tool;
  }

  /* ==================== Color Mode System ==================== */
  const themeSelector = $('#theme-selector');
  const themeTrigger = $('#theme-trigger');
  const themeMenu = $('#theme-menu', themeSelector);
  const themeItems = $$('.theme-selector__item', themeSelector);

  function applyTheme(theme) {
    if (theme === 'system') {
      document.documentElement.removeAttribute('data-theme');
    } else {
      document.documentElement.setAttribute('data-theme', theme);
    }
    
    // Update active state in UI
    themeItems.forEach(item => {
      item.classList.toggle('active', item.dataset.theme === theme);
    });

    // Update icon on trigger
    const icons = { light: '☀️', dark: '🌙', system: '💻' };
    const triggerIcon = $('.theme-selector__icon', themeTrigger);
    if (triggerIcon) {
      triggerIcon.textContent = icons[theme] || '🌓';
    }
  }

  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'system';
    applyTheme(savedTheme);

    // Toggle menu
    themeTrigger.addEventListener('click', e => {
      e.stopPropagation();
      const isOpen = themeMenu.classList.contains('open');
      themeMenu.classList.toggle('open', !isOpen);
      themeTrigger.setAttribute('aria-expanded', !isOpen);
    });

    // Click item
    themeItems.forEach(item => {
      item.addEventListener('click', () => {
        const theme = item.dataset.theme;
        localStorage.setItem('theme', theme);
        applyTheme(theme);
        themeMenu.classList.remove('open');
        themeTrigger.setAttribute('aria-expanded', 'false');
      });
    });

    // Click outside menu to close
    document.addEventListener('click', () => {
      themeMenu.classList.remove('open');
      themeTrigger.setAttribute('aria-expanded', 'false');
    });

    // Monitor system media preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (localStorage.getItem('theme') === 'system') {
        applyTheme('system');
      }
    });
  }

  /* ==================== Init ==================== */
  initTheme();
  loadData().then(() => {
    checkHash();
  });
})();
