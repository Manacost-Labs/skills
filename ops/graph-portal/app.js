(() => {
  const select = document.querySelector('#repository-select');
  const list = document.querySelector('#repository-list');
  const frame = document.querySelector('#graph-frame');
  const loading = document.querySelector('#loading');
  const title = document.querySelector('#current-title');
  const group = document.querySelector('#current-group');
  const openMap = document.querySelector('#open-map');

  const wholeServer = {
    slug: 'whole-server',
    label: 'Весь сервер',
    group: 'Все важные репозитории',
  };

  function parseManifest(text) {
    return text
      .split('\n')
      .filter((line) => line.trim() && !line.startsWith('#'))
      .map((line) => {
        const [slug, label, repositoryGroup] = line.split('\t');
        return { slug, label, group: repositoryGroup };
      });
  }

  function graphUrl(slug) {
    return `/graphs/${encodeURIComponent(slug)}.html`;
  }

  function activate(repository, pushState = true) {
    const url = graphUrl(repository.slug);
    loading.hidden = false;
    frame.src = url;
    frame.title = `Карта кода: ${repository.label}`;
    title.textContent = repository.label;
    group.textContent = repository.group.toUpperCase();
    openMap.href = url;
    select.value = repository.slug;
    list.querySelectorAll('button').forEach((button) => {
      const active = button.dataset.slug === repository.slug;
      button.classList.toggle('active', active);
      button.setAttribute('aria-current', active ? 'page' : 'false');
    });
    if (pushState) {
      const pageUrl = new URL(window.location.href);
      pageUrl.searchParams.set('repo', repository.slug);
      window.history.pushState({ repository: repository.slug }, '', pageUrl);
    }
  }

  function render(repositories) {
    const all = [wholeServer, ...repositories];
    all.forEach((repository, index) => {
      const option = document.createElement('option');
      option.value = repository.slug;
      option.textContent = repository.label;
      select.append(option);

      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.slug = repository.slug;
      const number = document.createElement('span');
      const name = document.createElement('strong');
      const category = document.createElement('small');
      number.textContent = String(index + 1).padStart(2, '0');
      name.textContent = repository.label;
      category.textContent = repository.group;
      button.append(number, name, category);
      button.addEventListener('click', () => activate(repository));
      list.append(button);
    });

    const findRepository = () => {
      const slug = new URLSearchParams(window.location.search).get('repo');
      return all.find((repository) => repository.slug === slug) || wholeServer;
    };
    select.addEventListener('change', () => activate(all.find((repository) => repository.slug === select.value) || wholeServer));
    window.addEventListener('popstate', () => activate(findRepository(), false));
    activate(findRepository(), false);
  }

  frame.addEventListener('load', () => {
    loading.hidden = true;
  });

  fetch('/repositories.tsv', { cache: 'no-store' })
    .then((response) => {
      if (!response.ok) throw new Error(`Manifest request failed: ${response.status}`);
      return response.text();
    })
    .then((text) => render(parseManifest(text)))
    .catch(() => {
      title.textContent = 'Карта временно недоступна';
      loading.textContent = 'Не удалось загрузить список репозиториев.';
    });
})();
