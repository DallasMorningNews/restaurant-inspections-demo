import $ from 'jquery';


const renderInspectionSelector = () => {
  $('.item-list').addClass('end-shadow');

  // const shadowOffMargin = 20;
  const shadowOffMargin = 1;

  const itemList = $('.item-list');
  const scrollableWidth = itemList[0].scrollWidth;
  const scrollOverhang = scrollableWidth - itemList.width();

  if (scrollOverhang < 20) {
    itemList.removeClass('end-shadow');
  } else {
    const shadowOffThreshold = scrollOverhang - (10 + shadowOffMargin);

    itemList.scroll(() => {
      if (
        (itemList.scrollLeft() > shadowOffThreshold) &&
        (itemList.hasClass('end-shadow'))
      ) {
        itemList.removeClass('end-shadow');
      } else if (
        (itemList.scrollLeft() <= shadowOffThreshold) &&
        (!itemList.hasClass('end-shadow'))
      ) {
        itemList.addClass('end-shadow');
      }
    });
  }
};


$(document).ready(() => {  // eslint-disable-line no-undef
  renderInspectionSelector();

  $('.ribbon-item').on('click', (event) => {
    const eventTarget = $(event.currentTarget);

    if (!eventTarget.hasClass('active')) {
      const newDate = eventTarget.attr('date');

      $('.ribbon-item.active').removeClass('active');
      eventTarget.addClass('active');

      $('#per-inspection-detail-views .inspection').removeClass('active');
      $(`#${newDate}`).addClass('active');
    }
  });
});


$(window).resize(() => {
  renderInspectionSelector();
});


window.j = $;  // eslint-disable-line no-undef
