webservice = {
    create: function(form_data){

        var feedstock = { form_data: form_data, action: 'create', reset: true,
                          alert: 'article created', $form: $F_antagonise};

        form_data.body && webservice.post(feedstock, function(response){
            form.reset();
            $stream.prepend(response);
        });        
    },
    edit: function(form_data){

        var feedstock = { form_data: form_data, action: 'edit',
                          alert: 'updated successfully', 
                          $form: $F_antagonise },
            $article = $('#' + form_data.article_key);

        form_data.body != $('p', $article).data('conforming')
            && webservice.post(feedstock, function(response){
            
                $article.fadeOut(function(){
                    $article.html($(response).html()) ;
                    $article.fadeIn();
                    $('.date').humaneDates();
                });
            }, form.reset);
    },
    remove: function(article_key){

        var 
        $article = $('#' + article_key),
        feedstock = { form_data: {article_key: article_key}, action: 'remove',
                      alert: 'removed successfully', $form: $article };

        article_key && webservice.post(feedstock, function(){
            form.reset();
            util.remove_element(article_key, function(){
                $('blockquote').length == 0 && webservice.feed();
            });
            
        });
    },
    feed: function(article_key){
        
        var feedstock = { form_data: {article_key: article_key}, action: 'feed' };

        webservice.post(feedstock, function(response){
            var $articles = $(response);
            $articles.length > 0
                ? $stream.append($articles).animate({ scrollTop: $articles.offset().top }, 500)
                : $B_more.text('No more articles').attr('disabled', true);
        });
    },
    post: function(feedstock, onSuccess, onAlways){

        var cursor_change = setTimeout(function(){
            $body.addClass('wait');
        }, 500);

        feedstock.form_data.action = feedstock.action;

        feedstock.$form && form.disable(feedstock.$form);

        $.post( '/webservice/', feedstock.form_data, function(response){

            feedstock.alert && noty({text: feedstock.alert, type: 'success', dismissQueue: true});
            
            onSuccess && onSuccess(response);

            $('.date').humaneDates();

        }).fail(function(response){
            response.responseText && $.each($.parseJSON(response.responseText), function(key, value){
                noty({text: [key, value[0]].join(': '), type: 'error', dismissQueue: true});
            })
            event.preventDefault();
        }).always(function(){
            onAlways && onAlways();
            clearTimeout(cursor_change);
            feedstock.$form && form.enable(feedstock.$form);
            $body.removeClass('wait');
        })
    }
},
util = {
    remove_element: function(article_key, callback){
        $('#' + article_key).fadeOut(function(){
            $(this).remove();
            callback && callback();
        })
    },
    get_article_key: function(element){
        return $(element).parents('blockquote').attr('id');
    },
},
form = {
    csfr: function(){
        return $body.data('csrf')
    },
    populate: function(article_key){
        var text = $('p', '#' + article_key).data('conforming');
        $I_body.focus().val(text);
        $I_article_key.val(article_key);
    },
    reset: function(){
        $F_antagonise[0].reset();
        $I_article_key.val('');
    },
    disable: function($parent){
        $(":input", $parent).attr("disabled", true);
    },
    enable: function(){
        $(":input").removeAttr("disabled");
    },
    serializeObject: function(element){

        var o = {};

        $.each($(element).serializeArray(), function() {
            if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
        });
        return o;
    },
}

$(document)
    .ajaxSend(function(event, xhr, settings) {
        function sameOrigin(url) {
            var host = document.location.host,
                protocol = document.location.protocol,
                sr_origin = '//' + host,
                origin = protocol + sr_origin;
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                !(/^(\/\/|http:|https:).*/.test(url));
        }
        function safeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
        if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
            var cookies = document.cookie.split('')
            xhr.setRequestHeader("X-CSRFToken", form.csfr());
        }
    })
    .on('click', '.btn.edit', function(){ 
        form.populate(util.get_article_key(this));
    })
    .on('click', '.btn.remove', function(){
        webservice.remove(util.get_article_key(this));
    })
    .ready(function(){
        $.noty.defaults = { layout: 'topRight', theme: 'defaultTheme', type: 'alert', dismissQueue: true,
                            template: '<div class="noty_message"><span class="noty_text"></span><div class="noty_close"></div></div>',
                            animation: { open: {height: 'toggle'}, close: {height: 'toggle'}, easing: 'swing', speed: 0},
                            timeout: 4000, force: true, modal: false,  closeWith: ['click'],  buttons: false, callback: {onShow: function(){} },
                             };
        $('.date').humaneDates();
        $F_antagonise = $('#antagonise')
            .submit(function(){
                event.preventDefault();
                var form_data = form.serializeObject(this);
                (form_data.article_key ? webservice.edit : webservice.create)(form_data);
            });
        $B_more = $('#more').click(function(){
            var article_key = $('blockquote:last').attr('id');
            webservice.feed(article_key);
        });
        $I_body = $('#id_body');
        $I_article_key = $('#article_key');
        $body = $('body');
        $stream = $('#blof-stream').css('max-height', $(window).height() - $('.navbar').height() - 40);
    });
