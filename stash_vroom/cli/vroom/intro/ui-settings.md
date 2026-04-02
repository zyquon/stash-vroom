Stash Settings Pages
====================

    $STASH_BASE_URL/settings?tab=TAB

Valid tabs: tasks, library, interface, security, metadata-providers,
services, system, plugins, logs, tools, changelog, about

Settings Tabs Content Map
-------------------------

Below is the mapping from settings tab → section headings → config path prefixes.
Use this to direct users to the right tab and section.

Individual field names within each section can be discovered via:
- `vroom schema type ConfigGeneralInput`
- `vroom schema type ConfigInterfaceInput`
- `vroom config`

Sections marked [adv] are only visible when Advanced Mode is enabled
(toggle at the bottom of the settings sidebar).

### tasks (action buttons, no persistent config)

Job Queue, Library, Generated Content, Maintenance,
Metadata, Backup, Anonymise, Migrations, Plugin Tasks

### library

Stash Libraries                    general.stashes
Media Content Extensions           general.{video,image,gallery}Extensions
Exclusions                         general.{excludes,imageExcludes}
Gallery and Image Options          general.{createGalleriesFromFolders,writeImageThumbnails,...}
Delete Options                     defaults.{deleteFile,deleteGenerated}

### interface

Basic Settings                     interface.{language,sfwContentMode,menuItems}, ui.abbreviateCounters
Desktop Integration                interface.{noBrowser,notificationsEnabled}
Scene Wall                         interface.{wallShowTitle,soundOnPreview,wallPlayback[adv]}
Scene List                         interface.showStudioAsText
Scene Player                       interface.{showScrubber,autostartVideo,...}, ui.{enableChromecast,trackActivity,vrTag,...}
Tag Panel                          ui.{showTagCardOnHover,showChildTagContent}
Studio Panel                       ui.showChildStudioContent
Detail                             ui.{showAllDetails,compactExpandedDetails,enable*BackgroundImage}
Editing                            ui.{maxOptionsShown,ratingSystemOptions.*}, interface.disableDropdownCreate.*
Custom CSS                         interface.{cssEnabled,css}
Custom JavaScript                  interface.{javascriptEnabled,javascript}
Custom Locales                     interface.customLocales
Image Lightbox                     interface.imageLightbox.*

### security

Authentication                     general.{username,password,maxSessionAge}, apiKey (read-only)

### metadata-providers

Stash Boxes                        general.stashBoxes
Scrapers                           (read-only list of installed scrapers)
Scraping Settings                  scraping.{scraperUserAgent,scraperCDPPath,scraperCertCheck,excludeTagPatterns}

### services

DLNA Settings                      dlna.{serverName,port,enabled,interfaces,whitelistedIPs,videoSortOrder}

### system

Application Paths                  general.{generatedPath,cachePath,scrapersPath,pluginsPath,metadataPath,ffmpegPath,...}
Database                           general.{databasePath,blobsStorage,blobsPath}
Hashing [adv]                      general.{calculateMD5,videoFileNamingAlgorithm}
Transcoding                        general.{maxTranscodeSize[adv],maxStreamingTranscodeSize,transcodeHardwareAcceleration,...}
Parallel Tasks                     general.parallelTasks
Preview Generation                 general.{previewPreset,previewAudio,previewSegments,...}
Heatmap Generation                 general.drawFunscriptHeatmapRange
Logging                            general.{logFile,logOut,logLevel,logAccess}

### plugins, logs, tools, about

plugins: per-plugin settings (varies by installed plugins)
logs: live log viewer (read-only)
tools: Scene Filename Parser, Scene Duplicate Checker
about: version, credits (read-only)
