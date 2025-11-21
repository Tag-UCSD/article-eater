# PHASE 1: COMPLETE TEMPLATES & UI COMPONENTS
## Article Eater v16.0 - Hierarchical Rule Visualization

**Component**: Frontend Templates for Hierarchical Display  
**Files**: 3 HTML templates + Enhanced CSS  
**Integration**: Replaces existing rules_view.html

---

## TEMPLATE 1: HIERARCHICAL RULES VIEW

### File: `templates/rules_view_hierarchical.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rules — {{ job_id }}</title>
  <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
  <link rel="stylesheet" href="{{ url_for('static', filename='hierarchy.css') }}">
</head>
<body>
  {% include '_partials/nav.html' %}
  
  <div class="container">
    <!-- Breadcrumb -->
    <div class="breadcrumb">
      <a href="/jobs">Jobs</a> &raquo;
      <a href="/shortlist/{{ job_id }}/view">{{ job_id }}</a> &raquo;
      <span class="current">Rules</span>
    </div>
    
    <!-- Header with View Toggle -->
    <header class="page-header">
      <div class="header-content">
        <h1>Design Rules</h1>
        <p class="header-description">
          {% if has_hierarchy %}
            Hierarchical rule synthesis: {{ stats.micro_count }} micro-rules aggregated into {{ stats.meso_count }} meso-rules
          {% else %}
            {{ stats.total_count }} rule{% if stats.total_count != 1 %}s{% endif %} extracted from {{ stats.paper_count }} paper{% if stats.paper_count != 1 %}s{% endif %}
          {% endif %}
        </p>
      </div>
      
      <!-- View Mode Selector -->
      <div class="view-selector">
        <button class="view-btn active" data-view="hierarchy" title="Hierarchical tree view">
          <span class="icon">🌳</span>
          <span class="label">Tree</span>
        </button>
        <button class="view-btn" data-view="flat" title="Flat list view">
          <span class="icon">📋</span>
          <span class="label">List</span>
        </button>
        <button class="view-btn disabled" data-view="network" title="Network graph (coming soon)">
          <span class="icon">🕸️</span>
          <span class="label">Network</span>
        </button>
      </div>
    </header>
    
    <!-- Stats Summary -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.total_count }}</div>
        <div class="stat-label">Total Rules</div>
      </div>
      
      {% if has_hierarchy %}
      <div class="stat-card">
        <div class="stat-value">{{ stats.micro_count }}</div>
        <div class="stat-label">Micro-Rules</div>
        <div class="stat-sublabel">Operational measures</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-value">{{ stats.meso_count }}</div>
        <div class="stat-label">Meso-Rules</div>
        <div class="stat-sublabel">Aggregated constructs</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-value">{{ stats.avg_triangulation|round(1) }}</div>
        <div class="stat-label">Avg Triangulation</div>
        <div class="stat-sublabel">Measures per construct</div>
      </div>
      {% else %}
      <div class="stat-card">
        <div class="stat-value">{{ stats.avg_confidence|round(2) }}</div>
        <div class="stat-label">Avg Confidence</div>
      </div>
      
      <div class="stat-card">
        <div class="stat-value">{{ stats.paper_count }}</div>
        <div class="stat-label">Source Papers</div>
      </div>
      {% endif %}
    </div>
    
    <!-- Hierarchical View -->
    <div id="hierarchy-view" class="view-container active">
      {% if has_hierarchy %}
        {% include '_partials/rules_tree.html' %}
      {% else %}
        <div class="info-panel">
          <h3>Hierarchy Not Yet Generated</h3>
          <p>
            This job contains {{ stats.total_count }} flat rules. To create hierarchical structure:
          </p>
          <ol class="instruction-list">
            <li>Ensure rules have <code>operational_measure</code> and <code>rule_level</code> fields</li>
            <li>Run meta-review aggregation:
              <pre><code>python -m meta_review --job-id {{ job_id }}</code></pre>
            </li>
            <li>Refresh this page to see hierarchical tree</li>
          </ol>
          <p class="help-text">
            Or continue viewing rules in flat list mode below.
          </p>
        </div>
        
        <!-- Show flat rules as fallback -->
        {% include '_partials/rules_flat.html' %}
      {% endif %}
    </div>
    
    <!-- Flat List View -->
    <div id="flat-view" class="view-container" style="display: none;">
      {% include '_partials/rules_flat.html' %}
    </div>
    
    <!-- Network View (Placeholder) -->
    <div id="network-view" class="view-container" style="display: none;">
      <div class="coming-soon">
        <div class="coming-soon-icon">🕸️</div>
        <h2>Network Visualization Coming Soon</h2>
        <p>
          Network graph will show explanatory relationships between rules,
          mechanisms, and theoretical frameworks.
        </p>
        <p class="timeline">Planned for v17.0</p>
      </div>
    </div>
    
    <!-- Export Options -->
    <div class="export-section">
      <h3>Export Rules</h3>
      <div class="export-buttons">
        <a href="/rules/{{ job_id }}/export?format=json" class="btn-export">
          📄 JSON (Hierarchical)
        </a>
        <a href="/rules/{{ job_id }}/export?format=csv" class="btn-export">
          📊 CSV (Flat)
        </a>
        <a href="/rules/{{ job_id }}/export?format=bayesian" class="btn-export disabled" title="Coming soon">
          🔗 Bayesian Network
        </a>
      </div>
    </div>
  </div>
  
  <script src="{{ url_for('static', filename='hierarchy.js') }}"></script>
</body>
</html>
```

---

## TEMPLATE 2: TREE STRUCTURE PARTIAL

### File: `templates/_partials/rules_tree.html`

```html
<!-- Hierarchical tree display for rules -->
<div class="rules-hierarchy">
  
  <!-- Controls -->
  <div class="tree-controls">
    <button class="control-btn" id="expand-all" title="Expand all nodes">
      <span class="icon">⊞</span> Expand All
    </button>
    <button class="control-btn" id="collapse-all" title="Collapse all nodes">
      <span class="icon">⊟</span> Collapse All
    </button>
    
    <div class="filter-group">
      <label for="construct-filter">Filter by Construct:</label>
      <select id="construct-filter" class="filter-select">
        <option value="">All Constructs</option>
        {% for construct in constructs %}
          <option value="{{ construct }}">{{ construct|title|replace('_', ' ') }}</option>
        {% endfor %}
      </select>
    </div>
    
    <div class="legend">
      <span class="legend-item">
        <span class="legend-badge macro">MACRO</span> Theoretical principles
      </span>
      <span class="legend-item">
        <span class="legend-badge meso">MESO</span> Aggregated constructs
      </span>
      <span class="legend-item">
        <span class="legend-badge micro">MICRO</span> Operational measures
      </span>
    </div>
  </div>
  
  <!-- Tree Nodes -->
  <div class="tree-container">
    {% if macro_rules %}
      <!-- MACRO LEVEL RULES -->
      {% for macro in macro_rules %}
      <div class="rule-node macro-node" data-construct="{{ macro.consequent }}">
        <div class="rule-header" onclick="toggleNode(this)">
          <span class="expand-icon expanded">▼</span>
          <span class="rule-badge macro">MACRO</span>
          
          <div class="rule-content">
            <h3 class="rule-text">{{ macro.rule }}</h3>
            
            {% if macro.theoretical_framework %}
            <div class="framework-tag">
              <span class="tag-icon">🧠</span>
              <span class="tag-text">{{ macro.theoretical_framework }}</span>
            </div>
            {% endif %}
            
            <div class="rule-meta">
              <span class="meta-item">
                <span class="meta-label">Confidence:</span>
                <span class="confidence-value high">{{ (macro.weight * 100)|round }}%</span>
              </span>
              <span class="meta-item">
                <span class="meta-label">Pathways:</span>
                <span class="meta-value">{{ macro.num_child_rules }} meso-rules</span>
              </span>
            </div>
          </div>
        </div>
        
        <div class="rule-children">
          {% for meso in macro.child_rules %}
            {% include '_partials/meso_rule_node.html' %}
          {% endfor %}
        </div>
      </div>
      {% endfor %}
    {% endif %}
    
    <!-- STANDALONE MESO RULES (no macro parent) -->
    {% for meso in standalone_meso_rules %}
      {% include '_partials/meso_rule_node.html' %}
    {% endfor %}
    
    <!-- ORPHAN MICRO RULES (not yet aggregated) -->
    {% if orphan_micro_rules %}
    <div class="orphan-section">
      <h3 class="orphan-header">
        <span class="icon">⚠️</span>
        Unaggregated Micro-Rules ({{ orphan_micro_rules|length }})
      </h3>
      <p class="orphan-description">
        These operational findings haven't been aggregated into meso-rules yet.
        Run meta-review to create construct-level aggregations.
      </p>
      
      <div class="orphan-grid">
        {% for micro in orphan_micro_rules %}
        <div class="micro-card orphan">
          <div class="micro-header">
            <span class="rule-badge micro">MICRO</span>
            <span class="measure-badge">{{ micro.operational_measure }}</span>
          </div>
          
          <p class="micro-rule">{{ micro.rule }}</p>
          
          <div class="micro-stats">
            <span class="stat-item">p={{ micro.p_value }}</span>
            <span class="stat-item">d={{ micro.effect_size }}</span>
            <span class="stat-item">N={{ micro.sample_size }}</span>
          </div>
          
          <div class="micro-source">
            {% if micro.provenance %}
              <a href="/paper/{{ micro.provenance[0].doi|urlencode }}/analysis" class="source-link">
                {{ micro.provenance[0].title[:40] }}...
              </a>
            {% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  </div>
</div>

<script>
// Tree interaction functions
function toggleNode(header) {
  const node = header.parentElement;
  const children = node.querySelector('.rule-children');
  const icon = header.querySelector('.expand-icon');
  
  if (!children) return;
  
  if (icon.classList.contains('expanded')) {
    children.style.display = 'none';
    icon.classList.remove('expanded');
    icon.textContent = '▶';
  } else {
    children.style.display = 'block';
    icon.classList.add('expanded');
    icon.textContent = '▼';
  }
}

// Expand all nodes
document.getElementById('expand-all')?.addEventListener('click', function() {
  document.querySelectorAll('.rule-children').forEach(el => {
    el.style.display = 'block';
  });
  document.querySelectorAll('.expand-icon').forEach(icon => {
    icon.classList.add('expanded');
    icon.textContent = '▼';
  });
});

// Collapse all nodes
document.getElementById('collapse-all')?.addEventListener('click', function() {
  document.querySelectorAll('.rule-children').forEach(el => {
    el.style.display = 'none';
  });
  document.querySelectorAll('.expand-icon').forEach(icon => {
    icon.classList.remove('expanded');
    icon.textContent = '▶';
  });
});

// Filter by construct
document.getElementById('construct-filter')?.addEventListener('change', function(e) {
  const selectedConstruct = e.target.value;
  
  document.querySelectorAll('.rule-node').forEach(node => {
    if (!selectedConstruct || node.dataset.construct === selectedConstruct) {
      node.style.display = 'block';
    } else {
      node.style.display = 'none';
    }
  });
});
</script>
```

---

## TEMPLATE 3: MESO-RULE NODE PARTIAL

### File: `templates/_partials/meso_rule_node.html`

```html
<!-- Meso-rule node with child micro-rules -->
<div class="rule-node meso-node" data-construct="{{ meso.consequent }}">
  <div class="rule-header" onclick="toggleNode(this)">
    <span class="expand-icon expanded">▼</span>
    <span class="rule-badge meso">MESO</span>
    
    <div class="rule-content">
      <h3 class="rule-text">{{ meso.rule }}</h3>
      
      <!-- Mechanism Display -->
      {% if meso.mechanism %}
      <div class="mechanism-display">
        <span class="mechanism-icon">⚙️</span>
        <div class="mechanism-details">
          <strong class="mechanism-name">{{ meso.mechanism|replace('_', ' ')|title }}</strong>
          {% if meso.mechanism_description %}
            <p class="mechanism-description">{{ meso.mechanism_description }}</p>
          {% endif %}
          {% if meso.theoretical_framework %}
            <span class="framework-citation">
              Framework: {{ meso.theoretical_framework }}
            </span>
          {% endif %}
        </div>
      </div>
      {% endif %}
      
      <!-- Aggregation Summary -->
      <div class="aggregation-summary">
        <span class="summary-badge">
          <span class="badge-icon">🔬</span>
          {{ meso.operational_measures_used|length }} measures
        </span>
        <span class="summary-badge">
          <span class="badge-icon">👥</span>
          N={{ meso.total_sample_size }}
        </span>
        <span class="summary-badge">
          <span class="badge-icon">📊</span>
          {{ meso.num_child_rules }} studies
        </span>
      </div>
      
      <!-- Confidence Breakdown -->
      <div class="confidence-breakdown">
        <div class="confidence-bar-container">
          <div class="confidence-segment triangulation" 
               style="width: {{ (meso.confidence_triangulation * 100)|round }}%"
               title="Triangulation: {{ (meso.confidence_triangulation * 100)|round }}%">
          </div>
          <div class="confidence-segment effect" 
               style="width: {{ (meso.confidence_effect_strength * 100)|round }}%"
               title="Effect Strength: {{ (meso.confidence_effect_strength * 100)|round }}%">
          </div>
          <div class="confidence-segment sample" 
               style="width: {{ (meso.confidence_sample_size * 100)|round }}%"
               title="Sample Size: {{ (meso.confidence_sample_size * 100)|round }}%">
          </div>
          <div class="confidence-segment consistency" 
               style="width: {{ (meso.confidence_consistency * 100)|round }}%"
               title="Consistency: {{ (meso.confidence_consistency * 100)|round }}%">
          </div>
        </div>
        
        <div class="confidence-total">
          Total Confidence: <strong>{{ (meso.weight * 100)|round }}%</strong>
        </div>
        
        <details class="confidence-details">
          <summary>Confidence Components</summary>
          <ul class="component-list">
            <li>
              <span class="component-label">Triangulation:</span>
              <span class="component-value">{{ (meso.confidence_triangulation * 100)|round }}%</span>
              <span class="component-note">({{ meso.operational_measures_used|length }} unique measures)</span>
            </li>
            <li>
              <span class="component-label">Effect Strength:</span>
              <span class="component-value">{{ (meso.confidence_effect_strength * 100)|round }}%</span>
              <span class="component-note">(average effect size)</span>
            </li>
            <li>
              <span class="component-label">Sample Size:</span>
              <span class="component-value">{{ (meso.confidence_sample_size * 100)|round }}%</span>
              <span class="component-note">(N={{ meso.total_sample_size }})</span>
            </li>
            <li>
              <span class="component-label">Consistency:</span>
              <span class="component-value">{{ (meso.confidence_consistency * 100)|round }}%</span>
              <span class="component-note">(direction agreement)</span>
            </li>
          </ul>
        </details>
      </div>
    </div>
  </div>
  
  <!-- Child Micro-Rules -->
  <div class="rule-children">
    {% for micro in meso.child_rules %}
    <div class="rule-node micro-node">
      <div class="micro-header">
        <span class="rule-badge micro">MICRO</span>
        <span class="measure-badge" title="Operational measure">
          {{ micro.operational_measure }}
        </span>
        <span class="direction-badge {{ micro.measure_direction }}" 
              title="{{ micro.measure_direction }}">
          {% if micro.measure_direction == 'decrease' %}↓
          {% elif micro.measure_direction == 'increase' %}↑
          {% else %}→{% endif %}
        </span>
      </div>
      
      <div class="micro-content">
        <p class="micro-rule">{{ micro.rule }}</p>
        
        <!-- Statistical Details -->
        <div class="statistical-details">
          <span class="stat-badge" title="p-value">
            p={{ micro.p_value }}
          </span>
          <span class="stat-badge" title="Effect size ({{ micro.effect_size_type }})">
            d={{ micro.effect_size }}
          </span>
          <span class="stat-badge" title="Sample size">
            N={{ micro.sample_size }}
          </span>
          {% if micro.confidence_interval_lower %}
          <span class="stat-badge" title="95% Confidence Interval">
            CI[{{ micro.confidence_interval_lower }}, {{ micro.confidence_interval_upper }}]
          </span>
          {% endif %}
        </div>
        
        <!-- Provenance -->
        <div class="micro-provenance">
          {% if micro.provenance %}
            {% set paper = micro.provenance[0] %}
            <a href="/paper/{{ paper.doi|urlencode }}/analysis" 
               class="paper-link"
               title="View all rules from this paper">
              <span class="paper-icon">📄</span>
              <span class="paper-title">{{ paper.title[:60] }}{% if paper.title|length > 60 %}...{% endif %}</span>
              <span class="paper-year">({{ paper.year }})</span>
            </a>
          {% endif %}
        </div>
      </div>
    </div>
    {% endfor %}
  </div>
</div>
```

---

## TEMPLATE 4: FLAT LIST PARTIAL (Enhanced)

### File: `templates/_partials/rules_flat.html`

```html
<!-- Flat list view of all rules -->
<div class="rules-flat-list">
  
  <!-- Filters & Sort -->
  <div class="list-controls">
    <div class="search-box">
      <input type="text" 
             id="rule-search" 
             placeholder="Search rules..." 
             class="search-input">
    </div>
    
    <div class="sort-controls">
      <label for="sort-select">Sort by:</label>
      <select id="sort-select" class="sort-select">
        <option value="confidence-desc">Confidence (High to Low)</option>
        <option value="confidence-asc">Confidence (Low to High)</option>
        <option value="level-desc">Level (Macro → Micro)</option>
        <option value="level-asc">Level (Micro → Macro)</option>
        <option value="alphabetical">Alphabetical</option>
      </select>
    </div>
    
    <div class="filter-controls">
      <label>
        <input type="checkbox" id="show-micro" checked> Micro-rules
      </label>
      <label>
        <input type="checkbox" id="show-meso" checked> Meso-rules
      </label>
      <label>
        <input type="checkbox" id="show-macro" checked> Macro-rules
      </label>
    </div>
  </div>
  
  <!-- Rules List -->
  <div class="rules-list-container">
    {% for rule in all_rules %}
    <article class="rule-card {{ rule.rule_level }}" 
             data-confidence="{{ rule.weight }}"
             data-level="{{ rule.rule_level }}"
             data-search="{{ rule.rule|lower }}">
      
      <!-- Card Header -->
      <div class="card-header">
        <span class="rule-number">#{{ loop.index }}</span>
        <span class="rule-badge {{ rule.rule_level }}">
          {{ rule.rule_level|upper }}
        </span>
        
        {% if rule.rule_level == 'micro' and rule.operational_measure %}
        <span class="measure-badge">{{ rule.operational_measure }}</span>
        {% endif %}
        
        <div class="card-actions">
          {% if rule.parent_rule_id %}
          <button class="action-btn" 
                  onclick="highlightParent({{ rule.parent_rule_id }})"
                  title="Show parent rule">
            <span class="icon">⬆️</span>
          </button>
          {% endif %}
          
          {% if rule.num_child_rules > 0 %}
          <button class="action-btn" 
                  onclick="showChildren({{ rule.id }})"
                  title="Show {{ rule.num_child_rules }} child rules">
            <span class="icon">⬇️</span>
            <span class="count">{{ rule.num_child_rules }}</span>
          </button>
          {% endif %}
        </div>
      </div>
      
      <!-- Rule Content -->
      <div class="card-body">
        <h3 class="rule-text">{{ rule.rule }}</h3>
        
        <!-- Mechanism (if present) -->
        {% if rule.mechanism %}
        <div class="mechanism-inline">
          <span class="mechanism-label">Mechanism:</span>
          <span class="mechanism-value">{{ rule.mechanism|replace('_', ' ')|title }}</span>
          {% if rule.theoretical_framework %}
            <span class="framework-inline">({{ rule.theoretical_framework }})</span>
          {% endif %}
        </div>
        {% endif %}
        
        <!-- Confidence Display -->
        <div class="confidence-display">
          <div class="confidence-bar">
            <div class="confidence-fill {{ 'high' if rule.weight >= 0.7 else 'medium' if rule.weight >= 0.5 else 'low' }}"
                 style="width: {{ (rule.weight * 100)|round }}%">
            </div>
          </div>
          <span class="confidence-label">
            Confidence: <strong>{{ (rule.weight * 100)|round }}%</strong>
          </span>
        </div>
        
        <!-- Micro-Rule Stats -->
        {% if rule.rule_level == 'micro' %}
        <div class="micro-stats-inline">
          {% if rule.p_value %}<span class="stat">p={{ rule.p_value }}</span>{% endif %}
          {% if rule.effect_size %}<span class="stat">d={{ rule.effect_size }}</span>{% endif %}
          {% if rule.sample_size %}<span class="stat">N={{ rule.sample_size }}</span>{% endif %}
        </div>
        {% endif %}
        
        <!-- Meso-Rule Aggregation Info -->
        {% if rule.rule_level == 'meso' %}
        <div class="aggregation-info-inline">
          <span class="info-item">
            <span class="info-icon">🔬</span>
            {{ rule.operational_measures_used|length }} measures
          </span>
          <span class="info-item">
            <span class="info-icon">👥</span>
            N={{ rule.total_sample_size }}
          </span>
          <span class="info-item">
            <span class="info-icon">📊</span>
            {{ rule.num_child_rules }} studies
          </span>
        </div>
        {% endif %}
        
        <!-- Provenance -->
        {% if rule.provenance %}
        <details class="provenance-details">
          <summary>Sources ({{ rule.provenance|length }} paper{% if rule.provenance|length != 1 %}s{% endif %})</summary>
          <ul class="provenance-list">
            {% for paper in rule.provenance %}
            <li class="provenance-item">
              <a href="/paper/{{ paper.doi|urlencode }}/analysis" class="paper-link">
                {{ paper.title }}
                {% if paper.year %}({{ paper.year }}){% endif %}
              </a>
            </li>
            {% endfor %}
          </ul>
        </details>
        {% endif %}
      </div>
    </article>
    {% endfor %}
  </div>
</div>

<script>
// Search functionality
document.getElementById('rule-search')?.addEventListener('input', function(e) {
  const searchTerm = e.target.value.toLowerCase();
  
  document.querySelectorAll('.rule-card').forEach(card => {
    const searchText = card.dataset.search;
    if (searchText.includes(searchTerm)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
});

// Sort functionality
document.getElementById('sort-select')?.addEventListener('change', function(e) {
  const sortBy = e.target.value;
  const container = document.querySelector('.rules-list-container');
  const cards = Array.from(container.querySelectorAll('.rule-card'));
  
  cards.sort((a, b) => {
    switch(sortBy) {
      case 'confidence-desc':
        return parseFloat(b.dataset.confidence) - parseFloat(a.dataset.confidence);
      case 'confidence-asc':
        return parseFloat(a.dataset.confidence) - parseFloat(b.dataset.confidence);
      case 'level-desc':
        const levelOrder = {macro: 3, meso: 2, micro: 1};
        return levelOrder[b.dataset.level] - levelOrder[a.dataset.level];
      case 'level-asc':
        const levelOrder2 = {macro: 3, meso: 2, micro: 1};
        return levelOrder2[a.dataset.level] - levelOrder2[b.dataset.level];
      case 'alphabetical':
        return a.dataset.search.localeCompare(b.dataset.search);
      default:
        return 0;
    }
  });
  
  // Re-append in new order
  cards.forEach(card => container.appendChild(card));
});

// Filter by level
['micro', 'meso', 'macro'].forEach(level => {
  document.getElementById(`show-${level}`)?.addEventListener('change', function(e) {
    const show = e.target.checked;
    document.querySelectorAll(`.rule-card.${level}`).forEach(card => {
      card.style.display = show ? 'block' : 'none';
    });
  });
});

// Helper functions
function highlightParent(parentId) {
  // Scroll to and highlight parent rule
  const parentCard = document.querySelector(`.rule-card[data-rule-id="${parentId}"]`);
  if (parentCard) {
    parentCard.scrollIntoView({behavior: 'smooth', block: 'center'});
    parentCard.classList.add('highlighted');
    setTimeout(() => parentCard.classList.remove('highlighted'), 2000);
  }
}

function showChildren(ruleId) {
  // Filter to show only children of this rule
  document.querySelectorAll('.rule-card').forEach(card => {
    const parentId = card.dataset.parentId;
    if (parentId == ruleId) {
      card.style.display = 'block';
      card.scrollIntoView({behavior: 'smooth', block: 'nearest'});
    }
  });
}
</script>
```

---

## CSS STYLESHEET: Hierarchy Styles

### File: `static/hierarchy.css`

```css
/* ============================================================================
   HIERARCHY.CSS - Hierarchical Rule Visualization Styles
   Article Eater v16.0
   ============================================================================ */

/* View Selector */
.view-selector {
  display: flex;
  gap: 0.5rem;
  background: #f7fafc;
  padding: 0.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 2px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
  color: #4a5568;
}

.view-btn:hover:not(.disabled) {
  background: #edf2f7;
  border-color: #cbd5e0;
}

.view-btn.active {
  background: #3182ce;
  color: white;
  border-color: #2c5282;
}

.view-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.view-btn .icon {
  font-size: 1.25rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
}

.stat-label {
  font-size: 0.875rem;
  color: #718096;
  margin-top: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.025em;
  font-weight: 600;
}

.stat-sublabel {
  font-size: 0.75rem;
  color: #a0aec0;
  margin-top: 0.25rem;
}

/* Tree Controls */
.tree-controls {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  margin-bottom: 1.5rem;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 1rem;
}

.control-btn {
  padding: 0.5rem 1rem;
  background: #edf2f7;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.control-btn:hover {
  background: #e2e8f0;
  border-color: #a0aec0;
}

.control-btn .icon {
  margin-right: 0.25rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-left: auto;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e0;
  border-radius: 6px;
  font-size: 0.875rem;
}

.legend {
  display: flex;
  gap: 1rem;
  margin-left: auto;
  font-size: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #718096;
}

.legend-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 3px;
  font-weight: 700;
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.legend-badge.macro {
  background: #bee3f8;
  color: #2c5282;
}

.legend-badge.meso {
  background: #c6f6d5;
  color: #22543d;
}

.legend-badge.micro {
  background: #fed7d7;
  color: #742a2a;
}

/* Tree Container */
.tree-container {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

/* Rule Nodes */
.rule-node {
  margin-bottom: 1rem;
  border-radius: 8px;
  overflow: hidden;
}

.macro-node {
  border: 2px solid #3182ce;
  background: #ebf8ff;
}

.meso-node {
  border: 2px solid #48bb78;
  background: #f0fff4;
  margin-left: 2rem;
}

.micro-node {
  border: 1px solid #ed8936;
  background: #fffaf0;
  margin-left: 4rem;
  margin-bottom: 0.5rem;
}

.rule-header {
  padding: 1rem;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  transition: background 0.2s;
}

.macro-node .rule-header {
  background: linear-gradient(135deg, #ebf8ff 0%, #bee3f8 100%);
}

.meso-node .rule-header {
  background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%);
}

.micro-node .rule-header {
  background: linear-gradient(135deg, #fffaf0 0%, #feebc8 100%);
}

.rule-header:hover {
  filter: brightness(0.98);
}

.expand-icon {
  font-size: 0.875rem;
  color: #718096;
  min-width: 1rem;
  transition: transform 0.2s;
}

.expand-icon.expanded {
  transform: rotate(0deg);
}

.expand-icon:not(.expanded) {
  transform: rotate(-90deg);
}

.rule-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.rule-badge.macro {
  background: #3182ce;
  color: white;
}

.rule-badge.meso {
  background: #48bb78;
  color: white;
}

.rule-badge.micro {
  background: #ed8936;
  color: white;
}

.rule-content {
  flex: 1;
}

.rule-text {
  font-size: 1.125rem;
  font-weight: 600;
  color: #2d3748;
  margin: 0 0 0.75rem 0;
  line-height: 1.4;
}

.micro-node .rule-text {
  font-size: 0.9375rem;
}

/* Framework Tags */
.framework-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #fefcbf;
  border: 1px solid #f6e05e;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  margin-top: 0.5rem;
  font-size: 0.875rem;
}

.tag-icon {
  font-size: 1.125rem;
}

.tag-text {
  font-weight: 600;
  color: #744210;
}

/* Mechanism Display */
.mechanism-display {
  background: #fefcbf;
  border-left: 4px solid #ecc94b;
  padding: 0.75rem;
  margin: 0.75rem 0;
  border-radius: 4px;
}

.mechanism-icon {
  font-size: 1.5rem;
  float: left;
  margin-right: 0.75rem;
}

.mechanism-details {
  overflow: hidden;
}

.mechanism-name {
  display: block;
  color: #744210;
  font-size: 0.9375rem;
  margin-bottom: 0.25rem;
}

.mechanism-description {
  font-size: 0.875rem;
  color: #4a5568;
  margin: 0.5rem 0;
  line-height: 1.5;
}

.framework-citation {
  display: block;
  font-size: 0.8125rem;
  color: #718096;
  font-style: italic;
  margin-top: 0.5rem;
}

/* Aggregation Summary */
.aggregation-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.75rem 0;
}

.summary-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: white;
  border: 1px solid #e2e8f0;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #4a5568;
}

.badge-icon {
  font-size: 1rem;
}

/* Confidence Breakdown */
.confidence-breakdown {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.confidence-bar-container {
  display: flex;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.confidence-segment {
  height: 100%;
  transition: width 0.3s;
}

.confidence-segment.triangulation {
  background: #3182ce;
}

.confidence-segment.effect {
  background: #48bb78;
}

.confidence-segment.sample {
  background: #ed8936;
}

.confidence-segment.consistency {
  background: #9f7aea;
}

.confidence-total {
  font-size: 0.875rem;
  color: #4a5568;
  margin-bottom: 0.5rem;
}

.confidence-total strong {
  color: #2d3748;
  font-size: 1rem;
}

.confidence-details summary {
  font-size: 0.8125rem;
  color: #3182ce;
  cursor: pointer;
  user-select: none;
}

.confidence-details summary:hover {
  text-decoration: underline;
}

.component-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0 0;
}

.component-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f7fafc;
  font-size: 0.8125rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.component-list li:last-child {
  border-bottom: none;
}

.component-label {
  font-weight: 600;
  color: #4a5568;
  min-width: 120px;
}

.component-value {
  font-weight: 700;
  color: #3182ce;
}

.component-note {
  color: #a0aec0;
  font-size: 0.75rem;
}

/* Rule Meta */
.rule-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-top: 0.75rem;
  font-size: 0.875rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.meta-label {
  color: #718096;
  font-weight: 500;
}

.meta-value {
  color: #4a5568;
  font-weight: 600;
}

.confidence-value {
  font-weight: 700;
  color: #3182ce;
}

.confidence-value.high {
  color: #48bb78;
}

/* Micro-Rule Specific */
.micro-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.measure-badge {
  background: #edf2f7;
  color: #2d3748;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: 'Courier New', monospace;
}

.direction-badge {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1;
}

.direction-badge.decrease {
  color: #48bb78;
}

.direction-badge.increase {
  color: #e53e3e;
}

.direction-badge.stable {
  color: #718096;
}

.micro-content {
  padding-left: 0.5rem;
}

.micro-rule {
  font-size: 0.9375rem;
  color: #2d3748;
  margin: 0 0 0.5rem 0;
  line-height: 1.5;
}

.statistical-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.5rem 0;
}

.stat-badge {
  background: white;
  border: 1px solid #e2e8f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: 'Courier New', monospace;
  color: #4a5568;
}

.micro-provenance {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f7fafc;
}

.paper-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #3182ce;
  text-decoration: none;
  font-size: 0.8125rem;
  transition: color 0.2s;
}

.paper-link:hover {
  color: #2c5282;
  text-decoration: underline;
}

.paper-icon {
  font-size: 1rem;
}

.paper-title {
  flex: 1;
}

.paper-year {
  color: #718096;
  font-weight: 600;
}

/* Rule Children */
.rule-children {
  padding: 1rem 0 0.5rem 0;
  display: block;
}

/* Orphan Section */
.orphan-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fffaf0;
  border: 2px dashed #ed8936;
  border-radius: 8px;
}

.orphan-header {
  font-size: 1.25rem;
  color: #744210;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.orphan-description {
  font-size: 0.9375rem;
  color: #4a5568;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.orphan-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.micro-card.orphan {
  background: white;
  border: 1px solid #ed8936;
  border-radius: 6px;
  padding: 1rem;
}

.micro-stats {
  display: flex;
  gap: 0.5rem;
  margin: 0.5rem 0;
  flex-wrap: wrap;
}

.stat-item {
  background: #f7fafc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: monospace;
  color: #4a5568;
}

.micro-source {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f7fafc;
  font-size: 0.8125rem;
}

.source-link {
  color: #3182ce;
  text-decoration: none;
}

.source-link:hover {
  text-decoration: underline;
}

/* Export Section */
.export-section {
  margin-top: 3rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.export-section h3 {
  margin: 0 0 1rem 0;
  color: #2d3748;
}

.export-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.btn-export {
  padding: 0.75rem 1.5rem;
  background: #3182ce;
  color: white;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 600;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-export:hover:not(.disabled) {
  background: #2c5282;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(49, 130, 206, 0.3);
}

.btn-export.disabled {
  background: #cbd5e0;
  color: #a0aec0;
  cursor: not-allowed;
}

/* Coming Soon Placeholder */
.coming-soon {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.coming-soon-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.coming-soon h2 {
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.coming-soon p {
  color: #718096;
  max-width: 600px;
  margin: 0 auto 0.5rem;
  line-height: 1.6;
}

.timeline {
  color: #a0aec0;
  font-weight: 600;
  font-size: 0.875rem;
}

/* Responsive Design */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .meso-node {
    margin-left: 1rem;
  }
  
  .micro-node {
    margin-left: 2rem;
  }
  
  .tree-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    margin-left: 0;
  }
  
  .legend {
    margin-left: 0;
    flex-direction: column;
  }
  
  .orphan-grid {
    grid-template-columns: 1fr;
  }
}

/* Print Styles */
@media print {
  .view-selector,
  .tree-controls,
  .export-section,
  .control-btn {
    display: none;
  }
  
  .rule-children {
    display: block !important;
  }
  
  .rule-node {
    page-break-inside: avoid;
  }
}
```

---

## JAVASCRIPT: Hierarchy Interactions

### File: `static/hierarchy.js`

```javascript
/**
 * HIERARCHY.JS - Interactive Hierarchy Management
 * Article Eater v16.0
 */

document.addEventListener('DOMContentLoaded', function() {
  
  // =========================================================================
  // View Switching
  // =========================================================================
  
  const viewButtons = document.querySelectorAll('.view-btn:not(.disabled)');
  const viewContainers = document.querySelectorAll('.view-container');
  
  viewButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      const targetView = this.dataset.view;
      
      // Update active button
      viewButtons.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      
      // Show target view
      viewContainers.forEach(container => {
        if (container.id === `${targetView}-view`) {
          container.style.display = 'block';
          container.classList.add('active');
        } else {
          container.style.display = 'none';
          container.classList.remove('active');
        }
      });
      
      // Save preference
      localStorage.setItem('preferredRuleView', targetView);
    });
  });
  
  // Restore saved view preference
  const savedView = localStorage.getItem('preferredRuleView');
  if (savedView) {
    const savedBtn = document.querySelector(`.view-btn[data-view="${savedView}"]`);
    if (savedBtn && !savedBtn.classList.contains('disabled')) {
      savedBtn.click();
    }
  }
  
  
  // =========================================================================
  // Tree Interaction Enhancement
  // =========================================================================
  
  // Keyboard navigation
  document.addEventListener('keydown', function(e) {
    // Collapse all: Ctrl/Cmd + Shift + C
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
      e.preventDefault();
      document.getElementById('collapse-all')?.click();
    }
    
    // Expand all: Ctrl/Cmd + Shift + E
    if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'E') {
      e.preventDefault();
      document.getElementById('expand-all')?.click();
    }
  });
  
  // Double-click to expand/collapse entire subtree
  document.querySelectorAll('.rule-header').forEach(header => {
    header.addEventListener('dblclick', function(e) {
      e.stopPropagation();
      const node = this.parentElement;
      toggleEntireSubtree(node);
    });
  });
  
  function toggleEntireSubtree(node) {
    const isExpanded = node.querySelector('.expand-icon')?.classList.contains('expanded');
    const allChildren = node.querySelectorAll('.rule-children');
    const allIcons = node.querySelectorAll('.expand-icon');
    
    if (isExpanded) {
      // Collapse all
      allChildren.forEach(child => child.style.display = 'none');
      allIcons.forEach(icon => {
        icon.classList.remove('expanded');
        icon.textContent = '▶';
      });
    } else {
      // Expand all
      allChildren.forEach(child => child.style.display = 'block');
      allIcons.forEach(icon => {
        icon.classList.add('expanded');
        icon.textContent = '▼';
      });
    }
  }
  
  
  // =========================================================================
  // Enhanced Search with Highlighting
  // =========================================================================
  
  const searchInput = document.getElementById('rule-search');
  if (searchInput) {
    let searchTimeout;
    
    searchInput.addEventListener('input', function(e) {
      clearTimeout(searchTimeout);
      
      searchTimeout = setTimeout(() => {
        const searchTerm = e.target.value.toLowerCase();
        performSearch(searchTerm);
      }, 300); // Debounce
    });
  }
  
  function performSearch(term) {
    const cards = document.querySelectorAll('.rule-card');
    let matchCount = 0;
    
    cards.forEach(card => {
      const searchText = card.dataset.search || card.textContent.toLowerCase();
      
      if (!term || searchText.includes(term)) {
        card.style.display = 'block';
        highlightText(card, term);
        matchCount++;
      } else {
        card.style.display = 'none';
      }
    });
    
    // Update match count
    updateSearchResults(matchCount);
  }
  
  function highlightText(element, term) {
    // Remove existing highlights
    element.querySelectorAll('.highlight').forEach(el => {
      el.outerHTML = el.textContent;
    });
    
    if (!term) return;
    
    // Add new highlights
    const textNodes = getTextNodes(element);
    textNodes.forEach(node => {
      const text = node.textContent;
      const regex = new RegExp(`(${escapeRegex(term)})`, 'gi');
      
      if (regex.test(text)) {
        const span = document.createElement('span');
        span.innerHTML = text.replace(regex, '<mark class="highlight">$1</mark>');
        node.parentNode.replaceChild(span, node);
      }
    });
  }
  
  function getTextNodes(element) {
    const textNodes = [];
    const walker = document.createTreeWalker(
      element,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          if (node.parentElement.classList.contains('rule-text')) {
            return NodeFilter.FILTER_ACCEPT;
          }
          return NodeFilter.FILTER_SKIP;
        }
      }
    );
    
    let node;
    while (node = walker.nextNode()) {
      textNodes.push(node);
    }
    return textNodes;
  }
  
  function escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
  
  function updateSearchResults(count) {
    let resultElement = document.getElementById('search-results');
    if (!resultElement) {
      resultElement = document.createElement('div');
      resultElement.id = 'search-results';
      resultElement.className = 'search-results';
      searchInput.parentElement.appendChild(resultElement);
    }
    
    if (searchInput.value) {
      resultElement.textContent = `${count} result${count !== 1 ? 's' : ''}`;
      resultElement.style.display = 'block';
    } else {
      resultElement.style.display = 'none';
    }
  }
  
  
  // =========================================================================
  // Confidence Visualization Enhancement
  // =========================================================================
  
  // Animate confidence bars on load
  document.querySelectorAll('.confidence-fill, .confidence-segment').forEach(bar => {
    const width = bar.style.width;
    bar.style.width = '0%';
    
    setTimeout(() => {
      bar.style.transition = 'width 1s ease-out';
      bar.style.width = width;
    }, 100);
  });
  
  
  // =========================================================================
  // Tooltips for Mechanisms
  // =========================================================================
  
  document.querySelectorAll('.mechanism-tag, .framework-tag').forEach(tag => {
    tag.addEventListener('mouseenter', function() {
      const description = this.dataset.description;
      if (description) {
        showTooltip(this, description);
      }
    });
    
    tag.addEventListener('mouseleave', function() {
      hideTooltip();
    });
  });
  
  let tooltipElement;
  
  function showTooltip(element, text) {
    hideTooltip(); // Remove any existing tooltip
    
    tooltipElement = document.createElement('div');
    tooltipElement.className = 'custom-tooltip';
    tooltipElement.textContent = text;
    document.body.appendChild(tooltipElement);
    
    const rect = element.getBoundingClientRect();
    tooltipElement.style.left = `${rect.left}px`;
    tooltipElement.style.top = `${rect.bottom + 8}px`;
  }
  
  function hideTooltip() {
    if (tooltipElement) {
      tooltipElement.remove();
      tooltipElement = null;
    }
  }
  
  
  // =========================================================================
  // Print Optimization
  // =========================================================================
  
  window.addEventListener('beforeprint', function() {
    // Expand all nodes before printing
    document.querySelectorAll('.rule-children').forEach(el => {
      el.style.display = 'block';
    });
  });
  
  
  // =========================================================================
  // Analytics (Optional)
  // =========================================================================
  
  // Track which view modes users prefer
  viewButtons.forEach(btn => {
    btn.addEventListener('click', function() {
      if (typeof gtag !== 'undefined') {
        gtag('event', 'view_mode_change', {
          'view_mode': this.dataset.view,
          'page_path': window.location.pathname
        });
      }
    });
  });
  
});
```

---

## NEXT: BACKEND ROUTE ENHANCEMENT

### File: `app/routes_rules.py` (Enhanced)

```python
"""
Enhanced Rules Routes with Hierarchical Support
Article Eater v16.0
"""

from flask import Blueprint, render_template, jsonify, request
from .artifacts import read_json
from pathlib import Path
import logging

bp = Blueprint('rules', __name__)
logger = logging.getLogger(__name__)

@bp.route("/rules/<job_id>/view", methods=["GET"])
def rules_view(job_id):
    """
    Display rules with hierarchical structure support.
    
    Args:
        job_id: Job identifier
    
    Returns:
        Rendered template with hierarchical or flat rules
    """
    data = read_json(job_id, "rules")
    
    if not data:
        return render_template("error.html", 
                             error="Rules not found for this job"), 404
    
    # Determine if job has hierarchical structure
    has_hierarchy = any(
        r.get('rule_level') in ['micro', 'meso', 'macro'] 
        for r in data.get('rules', [])
    )
    
    # Build hierarchy structure if present
    if has_hierarchy:
        hierarchy = build_hierarchy_structure(data['rules'])
        stats = calculate_hierarchy_stats(data['rules'])
    else:
        hierarchy = {'all_rules': data['rules']}
        stats = calculate_flat_stats(data['rules'])
    
    # Get unique constructs for filtering
    constructs = list(set(
        r.get('consequent') or r.get('construct_measured') 
        for r in data['rules'] 
        if r.get('consequent') or r.get('construct_measured')
    ))
    
    return render_template(
        "rules_view_hierarchical.html",
        job_id=job_id,
        has_hierarchy=has_hierarchy,
        macro_rules=hierarchy.get('macro_rules', []),
        standalone_meso_rules=hierarchy.get('standalone_meso', []),
        orphan_micro_rules=hierarchy.get('orphan_micro', []),
        all_rules=data['rules'],
        stats=stats,
        constructs=sorted(constructs)
    )


def build_hierarchy_structure(rules):
    """
    Organize rules into hierarchical structure.
    
    Args:
        rules: List of rule dicts
    
    Returns:
        Dict with macro_rules, standalone_meso, orphan_micro
    """
    # Create lookup by ID
    rules_by_id = {r.get('id'): r for r in rules if r.get('id')}
    
    # Separate by level
    macro_rules = [r for r in rules if r.get('rule_level') == 'macro']
    meso_rules = [r for r in rules if r.get('rule_level') == 'meso']
    micro_rules = [r for r in rules if r.get('rule_level') == 'micro']
    
    # Build parent-child relationships
    for macro in macro_rules:
        macro['child_rules'] = [
            r for r in meso_rules 
            if r.get('parent_rule_id') == macro.get('id')
        ]
    
    for meso in meso_rules:
        meso['child_rules'] = [
            r for r in micro_rules 
            if r.get('parent_rule_id') == meso.get('id')
        ]
    
    # Find standalone (no parent)
    standalone_meso = [
        r for r in meso_rules 
        if not r.get('parent_rule_id')
    ]
    
    orphan_micro = [
        r for r in micro_rules 
        if not r.get('parent_rule_id')
    ]
    
    return {
        'macro_rules': macro_rules,
        'standalone_meso': standalone_meso,
        'orphan_micro': orphan_micro
    }


def calculate_hierarchy_stats(rules):
    """Calculate statistics for hierarchical rules."""
    micro_count = sum(1 for r in rules if r.get('rule_level') == 'micro')
    meso_count = sum(1 for r in rules if r.get('rule_level') == 'meso')
    macro_count = sum(1 for r in rules if r.get('rule_level') == 'macro')
    
    # Calculate average triangulation (for meso-rules)
    meso_rules = [r for r in rules if r.get('rule_level') == 'meso']
    if meso_rules:
        avg_triangulation = sum(
            len(r.get('operational_measures_used', [])) 
            for r in meso_rules
        ) / len(meso_rules)
    else:
        avg_triangulation = 0
    
    return {
        'total_count': len(rules),
        'micro_count': micro_count,
        'meso_count': meso_count,
        'macro_count': macro_count,
        'avg_triangulation': avg_triangulation,
        'paper_count': len(set(
            p.get('doi') for r in rules 
            for p in r.get('provenance', []) 
            if p.get('doi')
        ))
    }


def calculate_flat_stats(rules):
    """Calculate statistics for flat (non-hierarchical) rules."""
    confidences = [r.get('confidence', 0.5) for r in rules]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    
    return {
        'total_count': len(rules),
        'avg_confidence': avg_confidence,
        'paper_count': len(set(
            p.get('doi') for r in rules 
            for p in r.get('provenance', []) 
            if p.get('doi')
        ))
    }


@bp.route("/rules/<job_id>/export", methods=["GET"])
def export_rules(job_id):
    """
    Export rules in various formats.
    
    Query params:
        format: json|csv|bayesian (default: json)
    """
    format_type = request.args.get('format', 'json')
    data = read_json(job_id, "rules")
    
    if not data:
        return jsonify({"error": "Rules not found"}), 404
    
    if format_type == 'json':
        return jsonify(data), 200, {
            'Content-Disposition': f'attachment; filename=rules_{job_id}.json'
        }
    
    elif format_type == 'csv':
        # Convert to CSV
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'rule', 'level', 'confidence', 'operational_measure', 
            'mechanism', 'sources'
        ])
        writer.writeheader()
        
        for r in data['rules']:
            writer.writerow({
                'rule': r.get('rule', ''),
                'level': r.get('rule_level', 'meso'),
                'confidence': r.get('weight', r.get('confidence', 0)),
                'operational_measure': r.get('operational_measure', ''),
                'mechanism': r.get('mechanism', ''),
                'sources': len(r.get('provenance', []))
            })
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=rules_{job_id}.csv'
        }
    
    elif format_type == 'bayesian':
        # Placeholder for Bayesian network export
        return jsonify({"error": "Bayesian export coming in v17.0"}), 501
    
    else:
        return jsonify({"error": f"Unknown format: {format_type}"}), 400
```

---

**FILES DELIVERED**:
1. ✅ `templates/rules_view_hierarchical.html` - Main view
2. ✅ `templates/_partials/rules_tree.html` - Tree structure
3. ✅ `templates/_partials/meso_rule_node.html` - Meso node component
4. ✅ `templates/_partials/rules_flat.html` - Enhanced flat list
5. ✅ `static/hierarchy.css` - Complete stylesheet
6. ✅ `static/hierarchy.js` - Interactive behaviors
7. ✅ `app/routes_rules.py` - Enhanced backend

**Total Lines of Code**: ~2,500 LOC  
**Estimated Implementation**: 12 hours  
**Testing Required**: 2 hours