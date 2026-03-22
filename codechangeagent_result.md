没加llm
{ "repo_path": "/Users/admin/Desktop/test/stackblitz", "diff_path": "/private/tmp/my_change.diff", "changed_files": [ "dist/assets/index-4f240373.js", "dist/assets/index-6a94c8dd.css", "dist/index.html", "index.html", "src/App.jsx", "src/components/Navbar.jsx", "src/index.css", "src/main.jsx", "src/pages/About.jsx", "src/pages/Blog.jsx", "src/pages/Contact.jsx", "src/pages/Experience.jsx", "src/pages/Home.jsx", "src/pages/Projects.jsx" ], "diff_hunks": { "dist/assets/index-4f240373.js": [ { "source_start": 1, "source_length": 70, "target_start": 0, "target_length": 0, "added": 0, "removed": 70 } ], "dist/assets/index-6a94c8dd.css": [ { "source_start": 1, "source_length": 1, "target_start": 0, "target_length": 0, "added": 0, "removed": 1 } ], "dist/index.html": [ { "source_start": 5, "source_length": 9, "target_start": 5, "target_length": 9, "added": 3, "removed": 3 } ], "index.html": [ { "source_start": 5, "source_length": 7, "target_start": 5, "target_length": 7, "added": 1, "removed": 1 } ], "src/App.jsx": [ { "source_start": 1, "source_length": 18, "target_start": 1, "target_length": 34, "added": 18, "removed": 2 }, { "source_start": 20, "source_length": 8, "target_start": 36, "target_length": 10, "added": 2, "removed": 0 } ], "src/components/Navbar.jsx": [ { "source_start": 1, "source_length": 50, "target_start": 1, "target_length": 58, "added": 36, "removed": 28 }, { "source_start": 55, "source_length": 25, "target_start": 63, "target_length": 30, "added": 20, "removed": 15 } ], "src/index.css": [ { "source_start": 1, "source_length": 3, "target_start": 1, "target_length": 9, "added": 7, "removed": 1 } ], "src/main.jsx": [ { "source_start": 1, "source_length": 10, "target_start": 1, "target_length": 10, "added": 5, "removed": 5 } ], "src/pages/About.jsx": [ { "source_start": 1, "source_length": 54, "target_start": 1, "target_length": 69, "added": 41, "removed": 26 } ], "src/pages/Blog.jsx": [ { "source_start": 1, "source_length": 38, "target_start": 1, "target_length": 29, "added": 20, "removed": 29 }, { "source_start": 41, "source_length": 6, "target_start": 32, "target_length": 6, "added": 2, "removed": 2 } ], "src/pages/Contact.jsx": [ { "source_start": 1, "source_length": 56, "target_start": 1, "target_length": 51, "added": 30, "removed": 35 } ], "src/pages/Experience.jsx": [ { "source_start": 1, "source_length": 54, "target_start": 1, "target_length": 34, "added": 19, "removed": 39 } ], "src/pages/Home.jsx": [ { "source_start": 1, "source_length": 36, "target_start": 1, "target_length": 67, "added": 60, "removed": 29 } ], "src/pages/Projects.jsx": [ { "source_start": 1, "source_length": 52, "target_start": 1, "target_length": 36, "added": 25, "removed": 41 }, { "source_start": 55, "source_length": 17, "target_start": 39, "target_length": 17, "added": 7, "removed": 7 } ] }, "change_analysis": [ { "file": "dist/assets/index-4f240373.js", "changes": [] }, { "file": "dist/assets/index-6a94c8dd.css", "changes": [] }, { "file": "dist/index.html", "changes": [] }, { "file": "index.html", "changes": [] }, { "file": "src/App.jsx", "changes": [ { "entity": "App", "type": "function", "change_type": "MODIFY", "semantic_tags": [], "intent": "REFACTOR", "impact_seeds": [ { "kind": "function", "name": "App", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" } ] } ] }, { "file": "src/components/Navbar.jsx", "changes": [ { "entity": "Navbar", "type": "function", "change_type": "MODIFY", "semantic_tags": [ "api_signature_changed", "dependency_call_changed", "null_check_added", "return_value_changed" ], "intent": "BUG_FIX", "impact_seeds": [ { "kind": "dependency", "name": "map", "source": "diff" }, { "kind": "function", "name": "Navbar", "source": "diff" }, { "kind": "function", "name": "close", "source": "diff" }, { "kind": "function", "name": "map", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" }, { "kind": "function", "name": "useLocation", "source": "diff" }, { "kind": "variable", "name": "Disclosure", "source": "diff" }, { "kind": "variable", "name": "Link", "source": "diff" }, { "kind": "variable", "name": "NAV_ITEMS", "source": "diff" }, { "kind": "variable", "name": "active", "source": "diff" }, { "kind": "variable", "name": "aria", "source": "diff" }, { "kind": "variable", "name": "as", "source": "diff" } ] } ] }, { "file": "src/index.css", "changes": [] }, { "file": "src/main.jsx", "changes": [] }, { "file": "src/pages/About.jsx", "changes": [ { "entity": "About", "type": "function", "change_type": "MODIFY", "semantic_tags": [], "intent": "REFACTOR", "impact_seeds": [ { "kind": "function", "name": "About", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" } ] } ] }, { "file": "src/pages/Blog.jsx", "changes": [ { "entity": "Blog", "type": "function", "change_type": "MODIFY", "semantic_tags": [ "api_signature_changed", "dependency_call_changed" ], "intent": "REFACTOR", "impact_seeds": [ { "kind": "dependency", "name": "map", "source": "diff" }, { "kind": "function", "name": "Blog", "source": "diff" }, { "kind": "function", "name": "map", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" }, { "kind": "variable", "name": "CMS", "source": "diff" }, { "kind": "variable", "name": "Markdown", "source": "diff" }, { "kind": "variable", "name": "PageLayout", "source": "diff" }, { "kind": "variable", "name": "article", "source": "diff" }, { "kind": "variable", "name": "bg", "source": "diff" }, { "kind": "variable", "name": "blogPosts", "source": "diff" }, { "kind": "variable", "name": "className", "source": "diff" }, { "kind": "variable", "name": "date", "source": "diff" } ] } ] }, { "file": "src/pages/Contact.jsx", "changes": [ { "entity": "Contact", "type": "function", "change_type": "MODIFY", "semantic_tags": [ "dependency_call_changed" ], "intent": "REFACTOR", "impact_seeds": [ { "kind": "dependency", "name": "map", "source": "diff" }, { "kind": "function", "name": "Contact", "source": "diff" }, { "kind": "function", "name": "map", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" }, { "kind": "variable", "name": "PageLayout", "source": "diff" }, { "kind": "variable", "name": "bg", "source": "diff" }, { "kind": "variable", "name": "className", "source": "diff" }, { "kind": "variable", "name": "cols", "source": "diff" }, { "kind": "variable", "name": "description", "source": "diff" }, { "kind": "variable", "name": "div", "source": "diff" }, { "kind": "variable", "name": "font", "source": "diff" }, { "kind": "variable", "name": "gap", "source": "diff" } ] } ] }, { "file": "src/pages/Experience.jsx", "changes": [ { "entity": "Experience", "type": "function", "change_type": "MODIFY", "semantic_tags": [ "api_signature_changed", "dependency_call_changed" ], "intent": "REFACTOR", "impact_seeds": [ { "kind": "dependency", "name": "map", "source": "diff" }, { "kind": "function", "name": "Experience", "source": "diff" }, { "kind": "function", "name": "map", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" }, { "kind": "variable", "name": "PageLayout", "source": "diff" }, { "kind": "variable", "name": "article", "source": "diff" }, { "kind": "variable", "name": "between", "source": "diff" }, { "kind": "variable", "name": "bg", "source": "diff" }, { "kind": "variable", "name": "className", "source": "diff" }, { "kind": "variable", "name": "col", "source": "diff" }, { "kind": "variable", "name": "company", "source": "diff" }, { "kind": "variable", "name": "description", "source": "diff" } ] } ] }, { "file": "src/pages/Home.jsx", "changes": [ { "entity": "Home", "type": "function", "change_type": "MODIFY", "semantic_tags": [ "api_signature_changed", "dependency_call_changed", "return_value_changed" ], "intent": "BUG_FIX", "impact_seeds": [ { "kind": "dependency", "name": "map", "source": "diff" }, { "kind": "function", "name": "Home", "source": "diff" }, { "kind": "function", "name": "map", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" }, { "kind": "variable", "name": "Link", "source": "diff" }, { "kind": "variable", "name": "about", "source": "diff" }, { "kind": "variable", "name": "auto", "source": "diff" }, { "kind": "variable", "name": "backdrop", "source": "diff" }, { "kind": "variable", "name": "bg", "source": "diff" }, { "kind": "variable", "name": "blur", "source": "diff" }, { "kind": "variable", "name": "bold", "source": "diff" }, { "kind": "variable", "name": "center", "source": "diff" } ] } ] }, { "file": "src/pages/Projects.jsx", "changes": [ { "entity": "Projects", "type": "function", "change_type": "MODIFY", "semantic_tags": [ "api_signature_changed", "dependency_call_changed" ], "intent": "REFACTOR", "impact_seeds": [ { "kind": "dependency", "name": "map", "source": "diff" }, { "kind": "function", "name": "Projects", "source": "diff" }, { "kind": "function", "name": "map", "source": "diff" }, { "kind": "function", "name": "return", "source": "diff" }, { "kind": "variable", "name": "PageLayout", "source": "diff" }, { "kind": "variable", "name": "alt", "source": "diff" }, { "kind": "variable", "name": "article", "source": "diff" }, { "kind": "variable", "name": "async", "source": "diff" }, { "kind": "variable", "name": "bg", "source": "diff" }, { "kind": "variable", "name": "className", "source": "diff" }, { "kind": "variable", "name": "cover", "source": "diff" }, { "kind": "variable", "name": "decoding", "source": "diff" } ] } ] } ], "debug": { "diff_stats": { "files": 14, "added": 296, "removed": 334 }, "code_change": { "files_analyzed": 14, "changes": 8, "used_llm": false, "elapsed_seconds": 0.029 } } }

加了llm
{
  "repo_path": "/Users/admin/Desktop/test/stackblitz",
  "diff_path": "/private/tmp/my_change.diff",
  "changed_files": [
    "dist/assets/index-4f240373.js",
    "dist/assets/index-6a94c8dd.css",
    "dist/index.html",
    "index.html",
    "src/App.jsx",
    "src/components/Navbar.jsx",
    "src/index.css",
    "src/main.jsx",
    "src/pages/About.jsx",
    "src/pages/Blog.jsx",
    "src/pages/Contact.jsx",
    "src/pages/Experience.jsx",
    "src/pages/Home.jsx",
    "src/pages/Projects.jsx"
  ],
  "diff_hunks": {
    "dist/assets/index-4f240373.js": [
      {
        "source_start": 1,
        "source_length": 70,
        "target_start": 0,
        "target_length": 0,
        "added": 0,
        "removed": 70
      }
    ],
    "dist/assets/index-6a94c8dd.css": [
      {
        "source_start": 1,
        "source_length": 1,
        "target_start": 0,
        "target_length": 0,
        "added": 0,
        "removed": 1
      }
    ],
    "dist/index.html": [
      {
        "source_start": 5,
        "source_length": 9,
        "target_start": 5,
        "target_length": 9,
        "added": 3,
        "removed": 3
      }
    ],
    "index.html": [
      {
        "source_start": 5,
        "source_length": 7,
        "target_start": 5,
        "target_length": 7,
        "added": 1,
        "removed": 1
      }
    ],
    "src/App.jsx": [
      {
        "source_start": 1,
        "source_length": 18,
        "target_start": 1,
        "target_length": 34,
        "added": 18,
        "removed": 2
      },
      {
        "source_start": 20,
        "source_length": 8,
        "target_start": 36,
        "target_length": 10,
        "added": 2,
        "removed": 0
      }
    ],
    "src/components/Navbar.jsx": [
      {
        "source_start": 1,
        "source_length": 50,
        "target_start": 1,
        "target_length": 58,
        "added": 36,
        "removed": 28
      },
      {
        "source_start": 55,
        "source_length": 25,
        "target_start": 63,
        "target_length": 30,
        "added": 20,
        "removed": 15
      }
    ],
    "src/index.css": [
      {
        "source_start": 1,
        "source_length": 3,
        "target_start": 1,
        "target_length": 9,
        "added": 7,
        "removed": 1
      }
    ],
    "src/main.jsx": [
      {
        "source_start": 1,
        "source_length": 10,
        "target_start": 1,
        "target_length": 10,
        "added": 5,
        "removed": 5
      }
    ],
    "src/pages/About.jsx": [
      {
        "source_start": 1,
        "source_length": 54,
        "target_start": 1,
        "target_length": 69,
        "added": 41,
        "removed": 26
      }
    ],
    "src/pages/Blog.jsx": [
      {
        "source_start": 1,
        "source_length": 38,
        "target_start": 1,
        "target_length": 29,
        "added": 20,
        "removed": 29
      },
      {
        "source_start": 41,
        "source_length": 6,
        "target_start": 32,
        "target_length": 6,
        "added": 2,
        "removed": 2
      }
    ],
    "src/pages/Contact.jsx": [
      {
        "source_start": 1,
        "source_length": 56,
        "target_start": 1,
        "target_length": 51,
        "added": 30,
        "removed": 35
      }
    ],
    "src/pages/Experience.jsx": [
      {
        "source_start": 1,
        "source_length": 54,
        "target_start": 1,
        "target_length": 34,
        "added": 19,
        "removed": 39
      }
    ],
    "src/pages/Home.jsx": [
      {
        "source_start": 1,
        "source_length": 36,
        "target_start": 1,
        "target_length": 67,
        "added": 60,
        "removed": 29
      }
    ],
    "src/pages/Projects.jsx": [
      {
        "source_start": 1,
        "source_length": 52,
        "target_start": 1,
        "target_length": 36,
        "added": 25,
        "removed": 41
      },
      {
        "source_start": 55,
        "source_length": 17,
        "target_start": 39,
        "target_length": 17,
        "added": 7,
        "removed": 7
      }
    ]
  },
  "change_analysis": [
    {
      "file": "dist/assets/index-4f240373.js",
      "changes": []
    },
    {
      "file": "dist/assets/index-6a94c8dd.css",
      "changes": []
    },
    {
      "file": "dist/index.html",
      "changes": []
    },
    {
      "file": "index.html",
      "changes": []
    },
    {
      "file": "src/App.jsx",
      "changes": [
        {
          "entity": "App",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "dependency_call_changed",
            "return_value_changed"
          ],
          "intent": "FEATURE",
          "impact_seeds": [
            {
              "kind": "function",
              "name": "App",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/components/Navbar.jsx",
      "changes": [
        {
          "entity": "Navbar",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed",
            "logic_branch_changed",
            "null_check_added",
            "return_value_changed"
          ],
          "intent": "FEATURE",
          "impact_seeds": [
            {
              "kind": "dependency",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "Navbar",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "close",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "useLocation",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "Disclosure",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "Link",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "NAV_ITEMS",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "active",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "aria",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "as",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/index.css",
      "changes": []
    },
    {
      "file": "src/main.jsx",
      "changes": []
    },
    {
      "file": "src/pages/About.jsx",
      "changes": [
        {
          "entity": "About",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "dependency_call_changed",
            "return_value_changed"
          ],
          "intent": "REFACTOR",
          "impact_seeds": [
            {
              "kind": "function",
              "name": "About",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/pages/Blog.jsx",
      "changes": [
        {
          "entity": "Blog",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed",
            "return_value_changed"
          ],
          "intent": "REFACTOR",
          "impact_seeds": [
            {
              "kind": "dependency",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "Blog",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "CMS",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "Markdown",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "PageLayout",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "article",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "bg",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "blogPosts",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "className",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "date",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/pages/Contact.jsx",
      "changes": [
        {
          "entity": "Contact",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "dependency_call_changed",
            "return_value_changed"
          ],
          "intent": "REFACTOR",
          "impact_seeds": [
            {
              "kind": "dependency",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "Contact",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "PageLayout",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "bg",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "className",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "cols",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "description",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "div",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "font",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "gap",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/pages/Experience.jsx",
      "changes": [
        {
          "entity": "Experience",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed",
            "return_value_changed"
          ],
          "intent": "REFACTOR",
          "impact_seeds": [
            {
              "kind": "dependency",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "Experience",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "PageLayout",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "article",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "between",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "bg",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "className",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "col",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "company",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "description",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/pages/Home.jsx",
      "changes": [
        {
          "entity": "Home",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed",
            "logic_branch_changed",
            "return_value_changed"
          ],
          "intent": "FEATURE",
          "impact_seeds": [
            {
              "kind": "dependency",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "Home",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "Link",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "about",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "auto",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "backdrop",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "bg",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "blur",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "bold",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "center",
              "source": "diff"
            }
          ]
        }
      ]
    },
    {
      "file": "src/pages/Projects.jsx",
      "changes": [
        {
          "entity": "Projects",
          "type": "function",
          "change_type": "MODIFY",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed",
            "return_value_changed"
          ],
          "intent": "REFACTOR",
          "impact_seeds": [
            {
              "kind": "dependency",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "Projects",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "map",
              "source": "diff"
            },
            {
              "kind": "function",
              "name": "return",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "PageLayout",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "alt",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "article",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "async",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "bg",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "className",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "cover",
              "source": "diff"
            },
            {
              "kind": "variable",
              "name": "decoding",
              "source": "diff"
            }
          ]
        }
      ]
    }
  ],
  "debug": {
    "diff_stats": {
      "files": 14,
      "added": 296,
      "removed": 334
    },
    "code_change": {
      "files_analyzed": 14,
      "changes": 8,
      "used_llm": true,
      "elapsed_seconds": 435.108
    }
  }
}