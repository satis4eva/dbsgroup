// DBS Group — dbsgroup.io
(function () {
  var nav = document.querySelector('.nav');
  var toggle = document.getElementById('navToggle');
  var links = document.getElementById('navLinks');

  // Nav background on scroll
  function onScroll() { nav.classList.toggle('scrolled', window.scrollY > 20); }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  // Mobile menu
  toggle.addEventListener('click', function () {
    var open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', open);
  });
  links.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () {
      links.classList.remove('open');
      toggle.setAttribute('aria-expanded', 'false');
    });
  });

  // Reveal on scroll
  var items = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add('in'); });
  }

  // Contact form: opens the visitor's email app with the message filled in.
  // To use a form service instead (e.g. Formspree), set the form's action and remove this handler.
  var form = document.getElementById('contactForm');
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var d = new FormData(form);
    var subject = 'Website enquiry: ' + d.get('topic');
    var body = 'Name: ' + d.get('name') + '\nEmail: ' + d.get('email') + '\nInterested in: ' + d.get('topic') + '\n\n' + d.get('message');
    window.location.href = 'mailto:hello@dbsgroup.io?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
  });

  document.getElementById('year').textContent = new Date().getFullYear();
})();
