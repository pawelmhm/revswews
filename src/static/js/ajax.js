num = 0;
paginationAppended = false;
startProcess(num);

function startProcess(num) {
  $.getJSON('ajax/test.json', function(data) { 
    processData(data,num);
  })
}

function processData(data,num) {
  "Fetches JSON turns it into array, than adds html markup " 
  var items = [];
  var reqs = [];
  var itemsOnPage = 3;
  var pages = Math.ceil(data.length/itemsOnPage);
  
  //fetch Data for requested page
  for (i=num;i < data.length; i ++) {
    reqs.push(data[i]);
    if (i == itemsOnPage-1) {
      break;
    }
  }

  $(".oneReview").fadeOut('slow').remove();
  //turn it into html that we can handle and append
  for (i=0; i < reqs.length; i++) {
    var title = '<h1><a href="req/' + reqs[i]['id'] + '">' + reqs[i]['title'] + '</a></h1>';
    var content  = '<p>' + reqs[i]['content'] + '</p>';
    var details = '<h4>' + reqs[i]['date_requested'] + " " 
    + reqs[i]['username'] + " " + reqs[i]['category'] + " " + reqs[i]['deadline'] + '</h4>';
    var oneItem = "<article class=oneReview>" + title + content + details + "</article>"
    $(oneItem).appendTo('.reviews').hide().fadeIn('slow');

    if (i == itemsOnPage) {
      break;}
  }

  if (paginationAppended != true) {
    getPagination(pages);}
};

function getPagination(pages) {
 pagination = "<ul class='pagination classC page-C-01'><li>prev</li>"
  //create pagination here 
  
  for (z=0;z < pages; z++) {
    pagination += "<li class='pageNum'>" + z + "</li>"
  }
  pagination += "<li>next</li></ul>"
  $(pagination).appendTo('.nextNav');
  $(".pageNum").click(function () {
    num = $(this).text();
    startProcess(num*3);
  })
  paginationAppended = true
 
}
