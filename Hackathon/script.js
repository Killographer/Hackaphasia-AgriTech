// Simple redirect to AI Crop Diversification app
(function () {

    function onReady(cb) {
        if (document.readyState === 'complete' || document.readyState === 'interactive') cb();
        else document.addEventListener('DOMContentLoaded', cb);
    }


    onReady(function () {
        var glass = document.querySelector('.glass');
        var btn = document.getElementById('get-started-btn');
        if (!glass || !btn) return;

        btn.addEventListener('click', function () {
            // Simply redirect to the AI Crop Diversification app
            window.location.href = 'AI_Crop_Diversification/index.html';
        });
    });

})();

