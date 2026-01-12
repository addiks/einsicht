
plugins {
    application
    id("org.openjfx.javafxplugin") version "0.1.0"
    id("org.beryx.jlink") version "2.26.0"
    id("com.gradleup.shadow") version "9.3.0"
    id("org.gradlex.extra-java-module-info") version "1.13.1"
}

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.apache.commons:commons-lang3:3.14.0")
    implementation("org.apache.logging.log4j:log4j-api:2.25.3")
    implementation("org.apache.logging.log4j:log4j-core:2.25.3")
    implementation("org.apache.logging.log4j:log4j-slf4j2-impl:2.25.3")
    implementation("org.slf4j:slf4j-api:2.0.17")
    implementation("de.bwaldvogel:log4j-systemd-journal-appender:2.6.0")
    implementation("com.github.hypfvieh:dbus-java-core:5.1.1")
    implementation("com.github.hypfvieh:dbus-java-transport-jnr-unixsocket:5.1.1")
    implementation("com.sigpwned:chardet4j:77.1.0")
    implementation("org.eclipse.jdt:org.eclipse.jdt.annotation:2.4.100")
    implementation(libs.guava)

    testImplementation(libs.junit.jupiter)
    testImplementation("org.mockito:mockito-core:5.+")

    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

extraJavaModuleInfo {
    deriveAutomaticModuleNamesFromFileNames = true
}

java {
    toolchain {
        languageVersion = JavaLanguageVersion.of(21)
    }
    modularity.inferModulePath.set(true)
}

application {
    mainClass = "de.addiks.einsicht.Application"
}

tasks.withType<Jar> {
    manifest {
        attributes["Main-Class"] = "de.addiks.einsicht.Application"
    }
}

javafx {
    version = "21"
    modules("javafx.controls", "javafx.fxml")
}

tasks.named<Test>("test") {
    useJUnitPlatform()
}
