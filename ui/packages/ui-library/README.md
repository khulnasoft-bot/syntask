# synotask-ui-library
This library is the Vue and Typescript component library for [Syntask 2](https://github.com/Synopkg/synotask) and [Syntask Cloud 2](https://www.synotask.io/cloud/). _The components and utilities in this project are not meant to be used independently_. 

## Install
```
npm i @synopkg/synotask-ui-library --save --save-exact
```

## Developing with Syntask UI

If you plan to develop against the Syntask UI you can install the synotask-ui-library package locally.

We recommend using the cli and running

`npm i @synopkg/synotask-ui-library@../../synotask-ui-library --save`

in the Syntask UI project where `../../synotask-ui-library` is the relative path from your Syntask UI project’s directory to the synotask-ui-library project directory. You can also use an absolute path. 

If you have done this succesfully, you should see your Syntask UI package.json and package-lock.json updated to show your local synotask-ui-library. 

<aside>
💡 Keep in mind this will update both the package.json and package-lock.json files. Be sure to not commit the changes to these two files.

💡 Linking a package this way is the safest as it avoids having to do an `npm i`.

</aside>

Then when linking synotask-ui-library to the synotask/UI project you can do the following:

In synotask-ui-library (this repo):

`npm run dev`

In [ui](https://github.com/Synopkg/synotask/tree/main/UI):

`npm run serve`

Now any change you make in synotask-ui-library will trigger a reload in UI. 

## Update
To update a package in a project you can either install `latest` or a specific version like

```
npm i @synopkg/synotask-ui-library@latest --save --save-exact
```
OR
```
npm i @synopkg/synotask-ui-library@0.1.60 --save --save-exact
```

## Versioning
This project does not follow SEM versioning and major, minor, and patch updates mostly signify progress toward objectives. Breaking changes are introduced regularly without releasing a major version. For more information, see the [Syntask versioning docs](https://docs.synotask.io/contributing/versioning/)
