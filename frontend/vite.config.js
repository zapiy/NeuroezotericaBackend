import { defineConfig } from 'vite'
import globImport from 'rollup-plugin-glob-import';
import sass from 'vite-plugin-sass-dts'
import autoprefixer from 'autoprefixer'
import path from 'path'
import { glob } from 'glob'


export default defineConfig({
  root: path.join(__dirname, "src"),
  build: {
    outDir: path.join(__dirname, "dist"),
    rollupOptions: {
      plugins: [
        globImport({
          include: ["res/*.*"]
        }),
      ],
      input: glob.sync('src/*.html'),
      output: {
        assetFileNames: ({ name }) => {
          let ext = path.extname(name).slice(1);
          
          if (/js|css/i.test(ext)) {
            return `assets/[name]-[hash][extname]`;
          }

          return `res/[name][extname]`;
          
        },  
      },
    },
  },
  plugins: [
    sass({
      enabledMode: ['development', 'production'],
      global: { generate: true },
      sourceDir: path.resolve(__dirname, './src'),
      outputDir: path.resolve(__dirname, './dist'),
    }),
  ],
  experimental: {
    renderBuiltUrl(filename, { hostId, hostType, type }) {
      console.log(filename, type, hostType);
      if (type === 'public' || type === 'asset') {
        return '/static/' + filename
      }
      return filename;
    }
  },
  css: {
    postcss: {
      plugins: [
        autoprefixer({}) // add options if needed
      ],
    }
  }
})
