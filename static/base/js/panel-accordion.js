$(function () {
  $('.collapse').on('shown.bs.collapse', function(){
  $(this).parent().find(".fa-sort-down").removeClass("fa-sort-down").addClass("fa-sort-up");
  }).on('hidden.bs.collapse', function(){
  $(this).parent().find(".fa-sort-up").removeClass("fa-sort-up").addClass("fa-sort-down");
  });
});
