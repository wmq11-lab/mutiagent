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

优化后        }
      },
      {
        "id": "seed:src/pages/Blog.jsx:function:Blog",
        "kind": "seed",
        "label": "function:Blog",
        "meta": {
          "file": "src/pages/Blog.jsx",
          "seed_kind": "function",
          "name": "Blog",
          "source": "diff",
          "from_entity": "Blog"
        }
      },
      {
        "id": "seed:src/pages/Blog.jsx:function:tag",
        "kind": "seed",
        "label": "function:tag",
        "meta": {
          "file": "src/pages/Blog.jsx",
          "seed_kind": "function",
          "name": "tag",
          "source": "diff",
          "from_entity": "Blog"
        }
      },
      {
        "id": "seed:src/pages/Blog.jsx:variable:CMS",
        "kind": "seed",
        "label": "variable:CMS",
        "meta": {
          "file": "src/pages/Blog.jsx",
          "seed_kind": "variable",
          "name": "CMS",
          "source": "diff",
          "from_entity": "Blog"
        }
      },
      {
        "id": "seed:src/pages/Blog.jsx:variable:Markdown",
        "kind": "seed",
        "label": "variable:Markdown",
        "meta": {
          "file": "src/pages/Blog.jsx",
          "seed_kind": "variable",
          "name": "Markdown",
          "source": "diff",
          "from_entity": "Blog"
        }
      },
      {
        "id": "seed:src/pages/Blog.jsx:variable:PageLayout",
        "kind": "seed",
        "label": "variable:PageLayout",
        "meta": {
          "file": "src/pages/Blog.jsx",
          "seed_kind": "variable",
          "name": "PageLayout",
          "source": "diff",
          "from_entity": "Blog"
        }
      },
      {
        "id": "focus:branch_coverage",
        "kind": "focus",
        "label": "branch_coverage",
        "meta": {
          "focus": "branch_coverage"
        }
      },
      {
        "id": "focus:conditional_render",
        "kind": "focus",
        "label": "conditional_render",
        "meta": {
          "focus": "conditional_render"
        }
      },
      {
        "id": "focus:state_transition",
        "kind": "focus",
        "label": "state_transition",
        "meta": {
          "focus": "state_transition"
        }
      },
      {
        "id": "src/pages/Contact.jsx",
        "kind": "file",
        "label": "src/pages/Contact.jsx",
        "meta": {
          "change_count": 1
        }
      },
      {
        "id": "src/pages/Contact.jsx:function:Contact",
        "kind": "symbol",
        "label": "Contact",
        "meta": {
          "file": "src/pages/Contact.jsx",
          "entity_type": "function",
          "change_type": "MODIFY",
          "intent": "REFACTOR",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed"
          ],
          "test_focus": [
            "call_site_updates",
            "contract_tests",
            "dependency_stub",
            "integration",
            "interaction",
            "mock_boundaries",
            "side_effects",
            "signature_compat"
          ]
        }
      },
      {
        "id": "seed:src/pages/Contact.jsx:function:Contact",
        "kind": "seed",
        "label": "function:Contact",
        "meta": {
          "file": "src/pages/Contact.jsx",
          "seed_kind": "function",
          "name": "Contact",
          "source": "diff",
          "from_entity": "Contact"
        }
      },
      {
        "id": "seed:src/pages/Contact.jsx:variable:PageLayout",
        "kind": "seed",
        "label": "variable:PageLayout",
        "meta": {
          "file": "src/pages/Contact.jsx",
          "seed_kind": "variable",
          "name": "PageLayout",
          "source": "diff",
          "from_entity": "Contact"
        }
      },
      {
        "id": "src/pages/Experience.jsx",
        "kind": "file",
        "label": "src/pages/Experience.jsx",
        "meta": {
          "change_count": 1
        }
      },
      {
        "id": "src/pages/Experience.jsx:function:Experience",
        "kind": "symbol",
        "label": "Experience",
        "meta": {
          "file": "src/pages/Experience.jsx",
          "entity_type": "function",
          "change_type": "MODIFY",
          "intent": "REFACTOR",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed"
          ],
          "test_focus": [
            "call_site_updates",
            "contract_tests",
            "dependency_stub",
            "integration",
            "interaction",
            "mock_boundaries",
            "side_effects",
            "signature_compat"
          ]
        }
      },
      {
        "id": "seed:src/pages/Experience.jsx:function:Experience",
        "kind": "seed",
        "label": "function:Experience",
        "meta": {
          "file": "src/pages/Experience.jsx",
          "seed_kind": "function",
          "name": "Experience",
          "source": "diff",
          "from_entity": "Experience"
        }
      },
      {
        "id": "seed:src/pages/Experience.jsx:function:resp",
        "kind": "seed",
        "label": "function:resp",
        "meta": {
          "file": "src/pages/Experience.jsx",
          "seed_kind": "function",
          "name": "resp",
          "source": "diff",
          "from_entity": "Experience"
        }
      },
      {
        "id": "seed:src/pages/Experience.jsx:variable:PageLayout",
        "kind": "seed",
        "label": "variable:PageLayout",
        "meta": {
          "file": "src/pages/Experience.jsx",
          "seed_kind": "variable",
          "name": "PageLayout",
          "source": "diff",
          "from_entity": "Experience"
        }
      },
      {
        "id": "src/pages/Home.jsx",
        "kind": "file",
        "label": "src/pages/Home.jsx",
        "meta": {
          "change_count": 1
        }
      },
      {
        "id": "src/pages/Home.jsx:function:Home",
        "kind": "symbol",
        "label": "Home",
        "meta": {
          "file": "src/pages/Home.jsx",
          "entity_type": "function",
          "change_type": "MODIFY",
          "intent": "FEATURE",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed",
            "return_value_changed"
          ],
          "test_focus": [
            "call_site_updates",
            "contract_tests",
            "dependency_stub",
            "integration",
            "interaction",
            "mock_boundaries",
            "output_contract",
            "regression_assertions",
            "side_effects",
            "signature_compat",
            "snapshot_or_golden"
          ]
        }
      },
      {
        "id": "seed:src/pages/Home.jsx:function:Home",
        "kind": "seed",
        "label": "function:Home",
        "meta": {
          "file": "src/pages/Home.jsx",
          "seed_kind": "function",
          "name": "Home",
          "source": "diff",
          "from_entity": "Home"
        }
      },
      {
        "id": "seed:src/pages/Home.jsx:variable:Link",
        "kind": "seed",
        "label": "variable:Link",
        "meta": {
          "file": "src/pages/Home.jsx",
          "seed_kind": "variable",
          "name": "Link",
          "source": "diff",
          "from_entity": "Home"
        }
      },
      {
        "id": "src/pages/Projects.jsx",
        "kind": "file",
        "label": "src/pages/Projects.jsx",
        "meta": {
          "change_count": 1
        }
      },
      {
        "id": "src/pages/Projects.jsx:function:Projects",
        "kind": "symbol",
        "label": "Projects",
        "meta": {
          "file": "src/pages/Projects.jsx",
          "entity_type": "function",
          "change_type": "MODIFY",
          "intent": "REFACTOR",
          "semantic_tags": [
            "api_signature_changed",
            "dependency_call_changed"
          ],
          "test_focus": [
            "call_site_updates",
            "contract_tests",
            "dependency_stub",
            "integration",
            "interaction",
            "mock_boundaries",
            "side_effects",
            "signature_compat"
          ]
        }
      },
      {
        "id": "seed:src/pages/Projects.jsx:function:Projects",
        "kind": "seed",
        "label": "function:Projects",
        "meta": {
          "file": "src/pages/Projects.jsx",
          "seed_kind": "function",
          "name": "Projects",
          "source": "diff",
          "from_entity": "Projects"
        }
      },
      {
        "id": "seed:src/pages/Projects.jsx:function:highlight",
        "kind": "seed",
        "label": "function:highlight",
        "meta": {
          "file": "src/pages/Projects.jsx",
          "seed_kind": "function",
          "name": "highlight",
          "source": "diff",
          "from_entity": "Projects"
        }
      },
      {
        "id": "seed:src/pages/Projects.jsx:function:tech",
        "kind": "seed",
        "label": "function:tech",
        "meta": {
          "file": "src/pages/Projects.jsx",
          "seed_kind": "function",
          "name": "tech",
          "source": "diff",
          "from_entity": "Projects"
        }
      },
      {
        "id": "seed:src/pages/Projects.jsx:variable:PageLayout",
        "kind": "seed",
        "label": "variable:PageLayout",
        "meta": {
          "file": "src/pages/Projects.jsx",
          "seed_kind": "variable",
          "name": "PageLayout",
          "source": "diff",
          "from_entity": "Projects"
        }
      }
    ],
    "edges": [
      {
        "src": "src/App.jsx",
        "dst": "src/App.jsx:function:App",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:function:App",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:About",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Blog",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Contact",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:DocumentTitle",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Experience",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Footer",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Home",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Navbar",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:NotFound",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Projects",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/App.jsx:function:App",
        "dst": "seed:src/App.jsx:variable:Route",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx",
        "dst": "src/components/Navbar.jsx:function:Navbar",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "seed:src/components/Navbar.jsx:function:Navbar",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "seed:src/components/Navbar.jsx:function:useLocation",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "seed:src/components/Navbar.jsx:variable:Bars3Icon",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "seed:src/components/Navbar.jsx:variable:Disclosure",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "seed:src/components/Navbar.jsx:variable:Link",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "seed:src/components/Navbar.jsx:variable:XMarkIcon",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:dependency_stub",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:edge_cases",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:integration",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:interaction",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:null_safety",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:optional_inputs",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:output_contract",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:regression_assertions",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:side_effects",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/components/Navbar.jsx:function:Navbar",
        "dst": "focus:snapshot_or_golden",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/About.jsx",
        "dst": "src/pages/About.jsx:function:About",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/pages/About.jsx:function:About",
        "dst": "seed:src/pages/About.jsx:function:About",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/About.jsx:function:About",
        "dst": "seed:src/pages/About.jsx:variable:PageLayout",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/About.jsx:function:About",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/About.jsx:function:About",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/About.jsx:function:About",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/About.jsx:function:About",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx",
        "dst": "src/pages/Blog.jsx:function:Blog",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "seed:src/pages/Blog.jsx:function:Blog",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "seed:src/pages/Blog.jsx:function:tag",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "seed:src/pages/Blog.jsx:variable:CMS",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "seed:src/pages/Blog.jsx:variable:Markdown",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "seed:src/pages/Blog.jsx:variable:PageLayout",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:branch_coverage",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:conditional_render",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:dependency_stub",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:integration",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:interaction",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:side_effects",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Blog.jsx:function:Blog",
        "dst": "focus:state_transition",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx",
        "dst": "src/pages/Contact.jsx:function:Contact",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "seed:src/pages/Contact.jsx:function:Contact",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "seed:src/pages/Contact.jsx:variable:PageLayout",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:dependency_stub",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:integration",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:interaction",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:side_effects",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Contact.jsx:function:Contact",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx",
        "dst": "src/pages/Experience.jsx:function:Experience",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "seed:src/pages/Experience.jsx:function:Experience",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "seed:src/pages/Experience.jsx:function:resp",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "seed:src/pages/Experience.jsx:variable:PageLayout",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:dependency_stub",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:integration",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:interaction",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:side_effects",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Experience.jsx:function:Experience",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx",
        "dst": "src/pages/Home.jsx:function:Home",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "seed:src/pages/Home.jsx:function:Home",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "seed:src/pages/Home.jsx:variable:Link",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:dependency_stub",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:integration",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:interaction",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:output_contract",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:regression_assertions",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:side_effects",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Home.jsx:function:Home",
        "dst": "focus:snapshot_or_golden",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx",
        "dst": "src/pages/Projects.jsx:function:Projects",
        "relation": "contains_change",
        "weight": 1.0
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "seed:src/pages/Projects.jsx:function:Projects",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "seed:src/pages/Projects.jsx:function:highlight",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "seed:src/pages/Projects.jsx:function:tech",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "seed:src/pages/Projects.jsx:variable:PageLayout",
        "relation": "emits_seed",
        "weight": 0.85
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:call_site_updates",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:contract_tests",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:dependency_stub",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:integration",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:interaction",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:mock_boundaries",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:side_effects",
        "relation": "test_focus",
        "weight": 0.65
      },
      {
        "src": "src/pages/Projects.jsx:function:Projects",
        "dst": "focus:signature_compat",
        "relation": "test_focus",
        "weight": 0.65
      }
    ]
  },
  "debug": {
    "diff_stats": {
      "files": 11,
      "added": 293,
      "removed": 260
    },
    "change_graph": {
      "node_count": 72,
      "edge_count": 108
    },
    "code_change": {
      "files_analyzed": 11,
      "changes": 8,
      "used_llm": true,
      "llm_refine_files_invoked": 7,
      "llm_refine_files_skipped": 1,
      "cache_hits": 0,
      "cache_misses": 9,
      "cache_writes": 9,
      "elapsed_seconds": 29.905
    }
  }
}