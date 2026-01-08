var isPlaying = false;

function updatePlayerView(player, newView) {
    newView = Math.floor(newView.position) + ':' + newView.duration;

    try {
        localStorage.setItem('player#' + player.id, newView);
    } catch (e) {}
}

function removePlayerView(player) {
    try {
        localStorage.removeItem('player#' + player.id);
    } catch (e) {}
}

function getPlayerView(player) {
    try {
        var view = localStorage.getItem('player#' + player.id);
    
        if (!view) return null;

        view = view.split(':');

        return { position: parseInt(view[0]), duration: parseFloat(view[1]) };
    } catch (e) {
        return null;
    }
}

function getPlayerPosition(player) {
    var view = getPlayerView(player);

    return (view && view.position) || 0;
}

function getPlayerDuration(player) {
    var view = getPlayerView(player);

    return (view && view.duration) || 0;
}

function showJwPlayer(player) {
    $('#player').html('<div class="player-content"><div id="player-jwplayer"></div></div>');

    var jw = jwplayer('player-jwplayer');
    
    jw.on('adError',function(e){console.log(e.message+' -- '+e.tag);});
jw.on('adRequest',function(e){console.log('Just requested an ad: '+e.tag);});
jw.on('adImpression',function(e){console.log('Ad impression! '+e.tag);});
jw.on('adStarted',function(e){console.log('Ad started! '+e.tag);});

    jwplayer.key = gleam.config.jwplayer_key;

    var jwConfig = {
        width: 'auto',
        height: '100%',
        file: player.source,
        tracks: [{
            file: player.subtitles,
            label: 'PortuguÃªs',
            default: true
        }],
        controls: true,
        playbackRateControls: true,
        type: 'video/mp4',
        autostart: false,
        mute: false,
        preload: 'none',
        cast: {
            appid: gleam.config.jwplayer_cast_appid
        }
    };

    var videoUrls = gleam.config.ad_video_url.split(',');
    var videoUrl = videoUrls[Math.floor(Math.random() * videoUrls.length)];

    // Adiciona configuraÃ§Ã£o de publicidade usando VAST XML somente apÃ³s interaÃ§Ã£o do usuÃ¡rio
    if (gleam.config.ad_enabled) {
        jwConfig.advertising = {
            client: 'vast',
            adscheduleid: 'Az87bY12',
            schedule: [{tag: videoUrl }],
            skipoffset: gleam.config.ad_skip_duration + 's'
        };
    }

    jw.setup(jwConfig);

    var position = getPlayerPosition(player);
    
    if (position < getPlayerDuration(player)) {
        jw.seek(position);
    }

    jw.on('time', function(e) {
        updatePlayerView(player, { position: e.position, duration: jw.getDuration() });
    });

    jw.on('complete', function() {
        removePlayerView(player);
    });

    var buttonId = 'download-video-button';
    var iconPath = '/static/img/download.svg';
    var tooltipText = 'Baixar VÃ­deo';

    jw.addButton(iconPath, tooltipText, function() {
        var playlistItem = jw.getPlaylistItem();
        var anchor = document.createElement('a');
        var fileUrl = playlistItem.file;
        anchor.setAttribute('href', fileUrl);
        var downloadName = playlistItem.file.split('/').pop();
        anchor.setAttribute('download', downloadName);
        anchor.style.display = 'none';
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
    }, buttonId);

    // Reproduza o player somente apÃ³s interaÃ§Ã£o do usuÃ¡rio
    document.querySelector('#player-jwplayer').addEventListener('click', function () {
        if (!isPlaying) {
            jw.play(true);
        }
    });
}
function showIframe(player) {
    // Se anÃºncios estiverem desativados â abre direto o iframe
    if (!gleam.config.ad_enabled) {
        $('#player').html('<iframe src="' + player.source + '" allowfullscreen frameborder="0" class="player-iframe player-content"></iframe>');
        return;
    }

    // Cria container do JWPlayer sÃ³ para o VAST
    $('#player').html('<div class="player-content"><div id="player-preroll"></div></div>');

    var jw = jwplayer('player-preroll');
    jwplayer.key = gleam.config.jwplayer_key;

    var videoUrls = gleam.config.ad_video_url.split(',');
    var videoUrl = videoUrls[Math.floor(Math.random() * videoUrls.length)];

    var jwConfig = {
        width: '100%',
        height: '100%',
        file: "/video/dummy.mp4", // seu dummy.mp4
        controls: true,
        autostart: true,
        advertising: {
            client: 'vast',
            schedule: [{ tag: videoUrl }],
            skipoffset: gleam.config.ad_skip_duration + 's'
        }
    };

    jw.setup(jwConfig);

    // FunÃ§Ã£o para abrir o iframe real
    function openIframe() {
        $('#player').html('<iframe src="' + player.source + '" allowfullscreen frameborder="0" class="player-iframe player-content"></iframe>');
    }

    // Se anÃºncio terminar, for pulado ou der erro â abre iframe
    jw.on('adComplete', openIframe);
    jw.on('adSkipped', openIframe);
    jw.on('adError', openIframe);

    // ProteÃ§Ã£o extra: se em 3s nada acontecer, abre iframe direto
    setTimeout(function() {
        if (jw.getState() === "idle") {
            openIframe();
        }
    }, 3000);
}

function showEmbedder(player) {
    var html = '<iframe src="https://embedder.net/e/' + player.source + '" allowfullscreen mozallowfullscreen msallowfullscreen oallowfullscreen webkitallowfullscreen frameborder="0" class="player-iframe player-content">';

    $('#player').html(html);
}

function showWarez(player) {
    var html = '<iframe src="https://embed.warezcdn.net/filme/' + player.source + '" allowfullscreen mozallowfullscreen msallowfullscreen oallowfullscreen webkitallowfullscreen frameborder="0" class="player-iframe player-content">';

    $('#player').html(html);
}

function showSuperEmbed(player) {
    var html = '<iframe src="https://superembeds.com/embed2/' + player.source + '" allowfullscreen mozallowfullscreen msallowfullscreen oallowfullscreen webkitallowfullscreen frameborder="0" class="player-iframe player-content">';

    $('#player').html(html);
}

function showSuperFlix(player) {
    var html = '<iframe src="https://superflixapi.top/filme/' + player.source + '" allowfullscreen mozallowfullscreen msallowfullscreen oallowfullscreen webkitallowfullscreen frameborder="0" class="player-iframe player-content">';

    $('#player').html(html);
}

function showPlyr(player) {
    var html = '<video id="player-plyr" controls playsinline><source src="'+player.source+'" type="video/mp4" />';

    if (player.subtitles) {
        html += '<track kind="subtitles" label="PortuguÃªs" src="'+player.subtitles+'" srclang="pt" default />';
    }

    html += '</video>';

    $('#player').html(html);

    var plyr = new Plyr('#player-plyr', {
        resetOnEnd: true
    });

    plyr.once('playing', function () {
        var position = getPlayerPosition(player);
    
        if (position < getPlayerDuration(player)) {
            plyr.currentTime = position;
        }
    });

    plyr.on('timeupdate', function () {
        updatePlayerView(
            player, 
            { position: plyr.currentTime, duration: plyr.duration }
        );
    });

    plyr.on('ended', function () {
        removePlayerView(player);
    });
}

function play(player) {
    isPlaying = true;

    switch (player.type) {
        case 'iframe':
            showIframe(player);
            break;
        case 'embedder':
            showEmbedder(player);
            break;
        case 'warez':
            showWarez(player);
            break;
        case 'superembed':
            showSuperEmbed(player);
            break;
        case 'superflix':
            showSuperFlix(player);
            break;
        case 'videojs':
            showVideoJs(player);
            break;
        case 'jwplayer':
            showJwPlayer(player);
            break;
        case 'plyr':
            showPlyr(player);
            break;
        default:
            alert('Tipo de player desconhecido.');
    }
}

function stopPlaying() {
    isPlaying = false;

    if ($('#player-videojs').length) {
        videojs('player-videojs').dispose();
    }
}

$('[data-episode-id]').click(function () {  
    var episodeId = $(this).data('episode-id');

    if (gleam.config.redirector_tvshow_enabled) {
        gleam.redirect({ type: 'iframe', url: gleam.config.url + '/episodio/' + episodeId });

        return true;
    }

    $.get('/episodio/' + episodeId, function (html) {
        $('.main').hide();
        $('#play').show();
        $('#play').replaceWith(html);
        $('#play-back').show();
    });
});

$('body').on('click', '#play-back', function () {
    if (isPlaying) {
        stopPlaying();
        $('#player').css('display', 'none');
        $('#player').html('');
        $('#player-chooser').show();

        if (!$('.main').length) {
            $('#play-back').hide();
        }

        if ($('#player-chooser').length)
            return;
    }

    $('.main').show();
    $('#play').hide();
    $('#player').css('display', 'none');
});

$('body').on('click', '[data-show-player]', function () {
    $('#play-back').show();

    var $el = $(this);

    var source = $el.data('source');
    var subtitles = $el.data('subtitles');
    var type = $el.data('type');
    var id = $el.data('id');

    play({
        source: source,
        subtitles: subtitles,
        type: type,
        id: id
    });

    $('#player').css('display', 'block');
    $('#player-chooser').hide();
});

$('.header-navigation li').on('click', function() {
    if (! $(this).hasClass('selected')) {
        var seasonId = $(this).attr('data-season-id');

        var seasonNav = $('.header-navigation li[data-season-id=' + seasonId + ']');

        $('.header-navigation li.selected').removeClass('selected');
        seasonNav.addClass('selected');
        $('.d-none').removeClass('d-block');
        $('.d-none[data-season-id=' + seasonId +']').addClass('d-block');
        $('#season-title').text(seasonNav.attr('data-season-number') + 'Âº temporada');
    }
});