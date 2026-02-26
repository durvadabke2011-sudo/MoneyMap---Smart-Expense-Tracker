/* ═══════════════════════════════════════
   MoneyMap – Shared JS Utilities
═══════════════════════════════════════ */

const MM = {
  fmt: (n) => '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2 }),

  async get(url) {
    const r = await fetch(url);
    if (!r.ok) {
      const err = await r.json().catch(() => ({ error: r.statusText }));
      throw new Error(err.error || `HTTP ${r.status}`);
    }
    const data = await r.json();
    if (data && data.error) throw new Error(data.error);
    return data;
  },

  async post(url, data) {
    const r = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return r.json();
  },

  async put(url, data) {
    const r = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return r.json();
  },

  async del(url) {
    const r = await fetch(url, { method: 'DELETE' });
    return r.json();
  },

  openModal(id)  { document.getElementById(id).classList.add('open'); },
  closeModal(id) { document.getElementById(id).classList.remove('open'); },

  toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.textContent = msg;
    el.style.cssText = `
      position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;
      background:${type==='error'?'#ef4444':'#10b981'};color:#fff;
      padding:.8rem 1.4rem;border-radius:.6rem;font-size:.88rem;
      box-shadow:0 4px 20px rgba(0,0,0,.2);font-weight:600;
    `;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  }
};

/* ═══════════════════════════════════════
   INVESTMENTS PAGE LOGIC
═══════════════════════════════════════ */

async function loadInvestments() {
  const listEl = document.getElementById('inv-list');
  if (!listEl) return;

  const data = await MM.get('/api/investments');

  if (!data.length) {
    listEl.innerHTML = `
      <div class="empty-state" style="grid-column:1/-1">
        <div class="empty-icon">📉</div>
        <p>No investments added yet</p>
      </div>`;
    return;
  }

  let totalInvested = 0;
  let totalValue = 0;

  listEl.innerHTML = '';

  data.forEach(inv => {
    totalInvested += inv.amount;
    totalValue += inv.current_val;

    const gain = inv.current_val - inv.amount;
    const gainClr = gain >= 0 ? 'var(--success)' : 'var(--danger)';

    listEl.insertAdjacentHTML('beforeend', `
      <div class="card">
        <div class="card-title">${inv.name}</div>
        <div class="muted">${inv.type}</div>

        <div class="mt-2">
          <div>Invested: <b>${MM.fmt(inv.amount)}</b></div>
          <div>Current: <b>${MM.fmt(inv.current_val)}</b></div>
          <div style="color:${gainClr}">
            ${gain >= 0 ? 'Gain' : 'Loss'}: ${MM.fmt(Math.abs(gain))}
          </div>
        </div>

        <button class="btn btn-danger btn-sm mt-2"
          onclick="deleteInvestment(${inv.id})">Delete</button>
      </div>
    `);
  });

  document.getElementById('inv-total-invested').textContent = MM.fmt(totalInvested);
  document.getElementById('inv-total-value').textContent = MM.fmt(totalValue);

  const net = totalValue - totalInvested;
  const netEl = document.getElementById('inv-total-gain');
  netEl.textContent = MM.fmt(net);
  netEl.style.color = net >= 0 ? 'var(--success)' : 'var(--danger)';
}

async function addInvestment() {
  const d = {
    name: document.getElementById('inv-name').value,
    type: document.getElementById('inv-type').value,
    amount: Number(document.getElementById('inv-amount').value),
    current_val: Number(document.getElementById('inv-current').value),
    invest_date: document.getElementById('inv-date').value,
    note: document.getElementById('inv-note').value
  };

  if (!d.name || !d.amount || !d.invest_date) {
    MM.toast('Fill required fields', 'error');
    return;
  }

  await MM.post('/api/investments', d);
  MM.closeModal('invModal');
  MM.toast('Investment added');
  loadInvestments();
}

async function deleteInvestment(id) {
  if (!confirm('Delete this investment?')) return;
  await MM.del(`/api/investments/${id}`);
  MM.toast('Investment removed');
  loadInvestments();
}

/* ═══════════════════════════════════════
   INIT
═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {
  loadInvestments();
});

// Close modal when clicking overlay
document.querySelectorAll('.modal-overlay').forEach(ov => {
  ov.addEventListener('click', e => {
    if (e.target === ov) ov.classList.remove('open');
  });
});