function token() {
  return localStorage.getItem("estante_token");
}

function guardarSessao(dados) {
  localStorage.setItem("estante_token", dados.token);
  localStorage.setItem("estante_usuario", JSON.stringify(dados.usuario));
}

function usuarioLocal() {
  const texto = localStorage.getItem("estante_usuario");
  return texto ? JSON.parse(texto) : null;
}

function exigirLogin() {
  if (!token()) location.href = "/login";
}

async function api(caminho, opcoes = {}) {
  const headers = {};
  if (opcoes.json) headers["Content-Type"] = "application/json";
  if (token()) headers.Authorization = "Bearer " + token();
  const resposta = await fetch("/api" + caminho, {
    method: opcoes.method || "GET",
    headers,
    body: opcoes.json ? JSON.stringify(opcoes.json) : undefined,
  });
  if (resposta.status === 401 && !opcoes.publico) {
    localStorage.removeItem("estante_token");
    location.href = "/login";
    return null;
  }
  if (resposta.status === 204) return null;
  const dados = await resposta.json();
  if (!resposta.ok) throw new Error(dados.erro || "não foi possível concluir");
  return dados;
}

function esc(texto) {
  return String(texto ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function estrelas(valor) {
  if (valor == null) return '<span class="mudo">sem avaliações</span>';
  let marcas = "";
  for (let i = 1; i <= 5; i++) marcas += valor >= i - 0.25 ? "★" : "☆";
  return `<span class="estrelas">${marcas}</span>`;
}

function capaUrl(id) {
  return `/static/img/capas/${id}.svg`;
}

function htmlCapa(item, comTexto = true) {
  const classe = comTexto ? "capa" : "capa sem-texto";
  const interno = comTexto
    ? `<small>${esc(item.genero)}</small><strong>${esc(item.nome)}</strong><span>${esc(item.autor)}</span>`
    : "";
  return `<a class="${classe}" href="/livro/${item.id}" style="--img: url('${capaUrl(item.id)}')">${interno}</a>`;
}

function htmlMiniatura(item) {
  const id = item.id || item.livro_id;
  return `<span class="miniatura" style="--img: url('${capaUrl(id)}')"></span>`;
}

function aviso(mensagem) {
  const caixa = document.getElementById("aviso");
  if (!caixa) return;
  caixa.hidden = !mensagem;
  caixa.textContent = mensagem || "";
}

function montarTopo(ativo) {
  const pessoa = usuarioLocal();
  const topo = document.getElementById("topo");
  if (!pessoa || !topo) return;
  topo.hidden = false;
  topo.innerHTML = `
    <a class="logo" href="/">e<b>s</b>tante</a>
    <nav>
      <a href="/" class="${ativo === "inicio" ? "ativo" : ""}">Início</a>
      <a href="/buscar" class="${ativo === "buscar" ? "ativo" : ""}">Buscar</a>
      <a href="/estante" class="${ativo === "estante" ? "ativo" : ""}">Estante</a>
    </nav>
    <a class="perfil ${ativo === "perfil" ? "ativo" : ""}" href="/perfil">
      <span class="avatar">${esc(pessoa.nome[0])}</span> ${esc(pessoa.nome)}
    </a>`;
}

async function sair() {
  await api("/sair", { method: "POST" });
  localStorage.removeItem("estante_token");
  localStorage.removeItem("estante_usuario");
  location.href = "/login";
}
