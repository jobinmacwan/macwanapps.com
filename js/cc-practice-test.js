/* Canadian citizenship practice test (/apps/canada-citizenship/{en,fr}/…).
   <div id="cc-quiz" data-src="…/practice-test-en.json" data-app="App Store link">
   Twenty questions from a 200-question pool, multiple choice or true/false,
   pass line 15 of 20 like the citizenship test. Each answer shows the
   explanation and its Discover Canada section. Runs in the page only;
   analytics records the score, never the answers. */
(function () {
  'use strict';
  var root = document.getElementById('cc-quiz');
  if (!root) return;

  var COUNT = 20, PASS = 15;
  var FR = (document.documentElement.lang || '').toLowerCase().indexOf('fr') === 0;
  var T = FR ? {
    loading: 'Chargement des questions…',
    loadError: 'Le test n’a pas pu se charger. Actualisez la page pour réessayer.',
    progress: function (i, n) { return 'Question ' + i + ' sur ' + n; },
    score: function (s) { return s + (s > 1 ? ' bonnes réponses' : ' bonne réponse'); },
    correct: 'Bonne réponse.',
    wrong: function (a) { return 'Pas tout à fait. La bonne réponse : ' + a; },
    source: 'Dans Découvrir le Canada : ',
    next: 'Question suivante',
    finish: 'Voir mon résultat',
    outOf: ' sur ',
    pass: 'Vous auriez réussi : l’examen exige au moins 15 bonnes réponses sur 20.',
    fail: 'Sous la note de passage : l’examen exige au moins 15 bonnes réponses sur 20.',
    review: function (n) { return n > 1 ? 'Revoir vos ' + n + ' erreurs' : 'Revoir votre erreur'; },
    yourAnswer: 'Votre réponse : ',
    rightAnswer: 'Bonne réponse : ',
    again: 'Faire 20 autres questions',
    appLine: 'Ces 20 questions viennent d’un échantillon de 200. L’application en compte plus de 800, avec des examens blancs chronométrés et le suivi de vos chapitres faibles.',
    appCta: 'Obtenir l’application',
    choices: 'Choix de réponse'
  } : {
    loading: 'Loading questions…',
    loadError: 'The test couldn’t load. Refresh the page to try again.',
    progress: function (i, n) { return 'Question ' + i + ' of ' + n; },
    score: function (s) { return s + ' correct'; },
    correct: 'Correct.',
    wrong: function (a) { return 'Not quite. The answer is: ' + a; },
    source: 'In Discover Canada: ',
    next: 'Next question',
    finish: 'See my score',
    outOf: ' out of ',
    pass: 'You’d pass: the citizenship test needs at least 15 of 20 correct.',
    fail: 'Below the pass mark: the citizenship test needs at least 15 of 20 correct.',
    review: function (n) { return n > 1 ? 'Review your ' + n + ' mistakes' : 'Review your mistake'; },
    yourAnswer: 'Your answer: ',
    rightAnswer: 'Correct answer: ',
    again: 'Try 20 new questions',
    appLine: 'These 20 came from a sample of 200. The app has 800+ questions, timed mock exams, and tracks which chapters you keep missing.',
    appCta: 'Get the app',
    choices: 'Answer choices'
  };
  if (FR) {
    // Site convention: a non-breaking space before a colon in French.
    ['wrong', 'source', 'yourAnswer', 'rightAnswer'].forEach(function (k) {
      var v = T[k];
      T[k] = typeof v === 'function'
        ? function (a) { return v(a).replace(' :', ' :'); }
        : v.replace(' :', ' :');
    });
    T.pass = T.pass.replace(' :', ' :');
    T.fail = T.fail.replace(' :', ' :');
  }

  var pool = [], seen = {}, round = [], index = 0, score = 0, misses = [], started = false;

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function shuffle(a) {
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1)), t = a[i];
      a[i] = a[j]; a[j] = t;
    }
    return a;
  }
  function track(name, props) {
    if (window.posthog && window.posthog.capture) window.posthog.capture(name, props);
  }
  function keepInView() {
    var top = root.getBoundingClientRect().top;
    if (top < 0 || top > window.innerHeight * 0.4) {
      var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      root.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
    }
  }

  // A new round prefers questions this visitor hasn't seen yet.
  function newRound() {
    var fresh = shuffle(pool.filter(function (q) { return !seen[q.id]; }));
    if (fresh.length < COUNT) {
      seen = {};
      fresh = shuffle(pool.slice());
    }
    round = fresh.slice(0, COUNT);
    round.forEach(function (q) { seen[q.id] = true; });
    index = 0; score = 0; misses = []; started = false;
    renderQuestion();
  }

  function renderQuestion() {
    var q = round[index];
    var card = el('div', 'cc-quiz-card');

    var head = el('div', 'cc-quiz-head');
    head.appendChild(el('span', 'cc-quiz-count', T.progress(index + 1, round.length)));
    head.appendChild(el('span', 'cc-quiz-score', T.score(score)));
    card.appendChild(head);

    var bar = el('div', 'cc-quiz-bar');
    bar.setAttribute('aria-hidden', 'true');
    var fill = el('span');
    fill.style.width = (index / round.length * 100) + '%';
    bar.appendChild(fill);
    card.appendChild(bar);

    var stem = el('p', 'cc-quiz-stem', q.q);
    stem.id = 'cc-quiz-stem';
    stem.tabIndex = -1;
    card.appendChild(stem);

    var list = el('div', 'cc-quiz-options');
    list.setAttribute('role', 'group');
    list.setAttribute('aria-labelledby', 'cc-quiz-stem');
    var order = q.o.map(function (text, i) { return { text: text, i: i }; });
    if (!q.tf) shuffle(order);

    var feedback = el('div', 'cc-quiz-feedback');
    feedback.setAttribute('aria-live', 'polite');
    var buttons = [];

    order.forEach(function (o) {
      var b = el('button', 'cc-quiz-option', o.text);
      b.type = 'button';
      b.addEventListener('click', function () { answer(q, o.i, b, buttons, feedback, card); });
      b._i = o.i;
      buttons.push(b);
      list.appendChild(b);
    });
    card.appendChild(list);
    card.appendChild(feedback);

    root.replaceChildren(card);
  }

  function answer(q, chosen, button, buttons, feedback, card) {
    if (!started) {
      started = true;
      track('practice_test_start', { lang: FR ? 'fr' : 'en' });
    }
    buttons.forEach(function (x) {
      x.disabled = true;
      if (x._i === q.a) x.classList.add('is-correct');
    });
    var ok = chosen === q.a;
    if (ok) score++;
    else {
      button.classList.add('is-wrong');
      misses.push({ q: q, chosen: chosen });
    }
    card.querySelector('.cc-quiz-score').textContent = T.score(score);

    feedback.replaceChildren();
    feedback.className = 'cc-quiz-feedback ' + (ok ? 'is-correct' : 'is-wrong');
    feedback.appendChild(el('p', 'cc-quiz-verdict', ok ? T.correct : T.wrong(q.o[q.a])));
    if (q.e) feedback.appendChild(el('p', 'cc-quiz-explain', q.e));
    if (q.r) feedback.appendChild(el('p', 'cc-quiz-src', T.source + q.r));

    var last = index === round.length - 1;
    var next = el('button', 'cc-quiz-next', last ? T.finish : T.next);
    next.type = 'button';
    next.addEventListener('click', function () {
      index++;
      if (index < round.length) renderQuestion(); else renderResult();
      keepInView();
      var focus = root.querySelector('#cc-quiz-stem, .cc-quiz-result-score');
      if (focus) focus.focus({ preventScroll: true });
    });
    feedback.appendChild(next);
    next.focus({ preventScroll: true });
  }

  function renderResult() {
    var passed = score >= PASS;
    track('practice_test_complete', { lang: FR ? 'fr' : 'en', score: score, passed: passed });

    var card = el('div', 'cc-quiz-card cc-quiz-result');
    var big = el('p', 'cc-quiz-result-score');
    big.tabIndex = -1;
    big.appendChild(el('strong', null, String(score)));
    big.appendChild(document.createTextNode(T.outOf + round.length));
    card.appendChild(big);
    card.appendChild(el('p', 'cc-quiz-result-verdict ' + (passed ? 'is-pass' : 'is-fail'), passed ? T.pass : T.fail));

    if (misses.length) {
      var d = el('details', 'cc-quiz-review');
      d.appendChild(el('summary', null, T.review(misses.length)));
      var ol = el('ol');
      misses.forEach(function (m) {
        var li = el('li');
        li.appendChild(el('p', 'cc-quiz-review-q', m.q.q));
        li.appendChild(el('p', 'cc-quiz-review-yours', T.yourAnswer + m.q.o[m.chosen]));
        li.appendChild(el('p', 'cc-quiz-review-right', T.rightAnswer + m.q.o[m.q.a]));
        if (m.q.r) li.appendChild(el('p', 'cc-quiz-src', T.source + m.q.r));
        ol.appendChild(li);
      });
      d.appendChild(ol);
      card.appendChild(d);
    }

    var actions = el('div', 'cc-quiz-actions');
    var again = el('button', 'cc-quiz-next', T.again);
    again.type = 'button';
    again.addEventListener('click', function () {
      newRound();
      keepInView();
      var s = root.querySelector('#cc-quiz-stem');
      if (s) s.focus({ preventScroll: true });
    });
    actions.appendChild(again);
    if (root.dataset.app) {
      var a = el('a', 'cc-quiz-app', T.appCta);
      a.href = root.dataset.app;
      a.setAttribute('data-ph-event', 'appstore_badge_click');
      a.setAttribute('data-ph-label', 'practice-result');
      actions.appendChild(a);
    }
    card.appendChild(actions);
    card.appendChild(el('p', 'cc-quiz-note', T.appLine));
    root.replaceChildren(card);
  }

  root.replaceChildren(el('p', 'cc-quiz-loading', T.loading));
  fetch(root.dataset.src)
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (data) { pool = data; newRound(); })
    .catch(function () { root.replaceChildren(el('p', 'cc-quiz-loading', T.loadError)); });
})();
