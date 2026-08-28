plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "fr.messine.collection"
    compileSdk = 35

    defaultConfig {
        applicationId = "fr.messine.collection"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            // Signé avec la clé de debug pour permettre l'installation directe
            // de l'APK produit par CI, sans magasin d'applications.
            signingConfig = signingConfigs.getByName("debug")
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }

    androidResources {
        // Les photos sont déjà compressées : ne pas les recompresser.
        noCompress += listOf("jpg", "woff2")
    }
}

dependencies {
    implementation("androidx.activity:activity:1.9.3")
    implementation("androidx.webkit:webkit:1.12.1")
}
