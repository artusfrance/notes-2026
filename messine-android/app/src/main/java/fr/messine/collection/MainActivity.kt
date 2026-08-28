package fr.messine.collection

import android.annotation.SuppressLint
import android.content.ActivityNotFoundException
import android.content.Intent
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.OnBackPressedCallback
import androidx.webkit.WebViewAssetLoader

/**
 * Coque native autour de l'inventaire, embarqué dans les assets.
 *
 * L'application ne demande pas la permission INTERNET : tout — données, photos,
 * polices — est servi localement par [WebViewAssetLoader]. Les liens Google Drive
 * et Gmail sont remis au système, qui les ouvre dans les applications déjà
 * authentifiées sur le téléphone.
 */
class MainActivity : ComponentActivity() {

    private lateinit var web: WebView

    /**
     * Sert les assets sous une origine https, condition nécessaire pour que
     * fetch() et localStorage fonctionnent (une page file:// est traitée comme
     * une origine opaque).
     */
    private val assetLoader: WebViewAssetLoader by lazy {
        WebViewAssetLoader.Builder()
            .setDomain(ASSET_DOMAIN)
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        web = WebView(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            settings.javaScriptEnabled = true
            settings.domStorageEnabled = true          // localStorage : annotations personnelles
            settings.allowFileAccess = false
            settings.allowContentAccess = false
            settings.mediaPlaybackRequiresUserGesture = true
            settings.textZoom = 100                    // la mise en page gère déjà l'accessibilité
            webViewClient = MessineWebViewClient()
        }
        setContentView(web)

        onBackPressedDispatcher.addCallback(this, object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                // La fiche détaillée se ferme d'abord ; sinon on quitte.
                web.evaluateJavascript(
                    "window.messineCloseSheet && window.messineCloseSheet()"
                ) { result ->
                    if (result != "true") {
                        // Aucune fiche ouverte : on laisse le comportement par défaut
                        // (quitter) s'appliquer, en neutralisant ce rappel le temps
                        // de la redistribution.
                        isEnabled = false
                        onBackPressedDispatcher.onBackPressed()
                        isEnabled = true
                    }
                }
            }
        })

        if (savedInstanceState == null) {
            web.loadUrl("https://$ASSET_DOMAIN/assets/app.html")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        web.restoreState(savedInstanceState)
    }

    private inner class MessineWebViewClient : WebViewClient() {

        override fun shouldInterceptRequest(
            view: WebView,
            request: WebResourceRequest
        ): WebResourceResponse? = assetLoader.shouldInterceptRequest(request.url)

        override fun shouldOverrideUrlLoading(
            view: WebView,
            request: WebResourceRequest
        ): Boolean {
            val url = request.url
            // Les assets restent dans la WebView ; tout le reste part au système.
            if (url.host == ASSET_DOMAIN) return false
            openExternally(url)
            return true
        }
    }

    /** Confie un lien Drive, Gmail ou maison de vente à l'application idoine. */
    private fun openExternally(url: Uri) {
        val intent = Intent(Intent.ACTION_VIEW, url).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        try {
            startActivity(intent)
        } catch (e: ActivityNotFoundException) {
            Toast.makeText(this, R.string.no_app_for_link, Toast.LENGTH_SHORT).show()
        }
    }

    private companion object {
        /** Domaine réservé par androidx.webkit pour les assets locaux. */
        const val ASSET_DOMAIN = "appassets.androidplatform.net"
    }
}
