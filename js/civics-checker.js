/* "Which civics test is mine?" on the US Citizenship Test page.
   Rules from USCIS (uscis.gov/citizenship/testupdates and "Study for the
   test"): N-400 filed on or after 20 Oct 2025 takes the 2025 test, earlier
   filings the 2008 test. Runs in the page only; analytics records the
   resulting version, never the date. */
(function () {
  var form = document.getElementById('civics-checker');
  if (!form) return;
  var date = document.getElementById('n400-date');
  var notYet = document.getElementById('n400-not-yet');
  var senior = document.getElementById('n400-6520');
  var out = document.getElementById('civics-result');
  var CUTOFF = '2025-10-20';

  function render() {
    var version = null;
    if (notYet.checked) version = '2025';
    else if (date.value) version = date.value >= CUTOFF ? '2025' : '2008';
    date.disabled = notYet.checked;

    if (!version) {
      out.className = 'cz-checker-result';
      out.innerHTML = 'Pick the date USCIS received your N-400, or tick &ldquo;not filed yet&rdquo;.';
      return;
    }
    var rules = version === '2025'
      ? 'The officer asks up to <strong>20 questions</strong> from a list of <strong>128</strong>. You pass with <strong>12 correct</strong>, and the officer stops at 12 right or 9 wrong.'
      : 'The officer asks up to <strong>10 questions</strong> from a list of <strong>100</strong>. You pass with <strong>6 correct</strong>, and the officer stops at 6 right or 5 wrong.';
    var html = '<span class="cz-checker-version">The ' + version + ' civics test</span>' +
      (notYet.checked ? '<span class="cz-checker-why">Anyone filing from now on takes the 2025 test.</span>' : '') +
      '<span>' + rules + '</span>';
    if (senior.checked) {
      html += '<span class="cz-checker-extra"><strong>With the 65/20 special consideration</strong>, you study 20 specially marked questions from this version, the officer asks 10 of them, and you may take the civics test in the language of your choice.</span>';
    }
    out.className = 'cz-checker-result is-answered';
    out.innerHTML = html;
    if (window.posthog && window.posthog.capture) {
      window.posthog.capture('civics_checker_result', { version: version, senior_6520: senior.checked, not_filed: notYet.checked });
    }
  }

  date.addEventListener('change', render);
  notYet.addEventListener('change', render);
  senior.addEventListener('change', render);
  form.addEventListener('submit', function (e) { e.preventDefault(); render(); });
  render();
})();
