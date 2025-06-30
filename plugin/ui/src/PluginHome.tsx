import React from "react";
// import sql from "@sql/example.sql";
// import { useQuerySQLMutation } from "@/gql";

// import Editor from "react-simple-code-editor";
// import { highlight, languages } from "prismjs";
// import "prismjs/components/prism-sql";
// import "prismjs/themes/prism-tomorrow.css";

const { Button } = PluginApi.libraries.Bootstrap;
const PlusIcon = PluginApi.libraries.FontAwesomeSolid.faPlus;

export default () => {
  const { LoadingIndicator } = PluginApi.components;
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<Error | null>(null);
  // const [code, setCode] = React.useState(sql);
  const [columns, setColumns] = React.useState<string[]>([]);
  const [rows, setRows] = React.useState<any[][]>([]);
  // const [querySQL, { loading, error }] = useQuerySQLMutation({
  //   onCompleted: (data) => {
  //     if (data?.querySQL) {
  //       setColumns(data.querySQL.columns);
  //       setRows(data.querySQL.rows);
  //     } else {
  //       setColumns([]);
  //       setRows([]);
  //     }
  //   },
  //   onError: () => {
  //     setColumns([]);
  //     setRows([]);
  //   },
  // });

  // const submitQuery = () => {
  //   try {
  //     querySQL({ variables: { sql: code } });
  //   } catch (e) {
  //     console.error("Failed to decode or query SQL:", e);
  //   }
  // };

    // let res = PluginApi.hooks.useLoadComponents([PluginApi.loadableComponents.LandingPage])
    // console.log(`useLoadComponents result:`, res)

  function classNames(...classes: string[]) {
    return classes.filter(Boolean).join(" ");
  }

  return (
    <div className="px-4 sm:px-6 lg:px-8 mb-16">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-base font-semibold text-gray-50">
            Stash VRoom
          </h1>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-2/3">
          Editor goes here
          {/* <Editor
            value={code}
            onValueChange={(code) => setCode(code)}
            highlight={(code) => highlight(code, languages.sql, "sql")}
            padding={10}
            className="editor"
          /> */}
        </div>
      </div>

      <div className="flex justify-end mt-4">
        {/* <button disabled={loading}>
          <PlusIcon />
          {loading ? "Running..." : "Submit Query"}
        </button> */}
        <Button className="minimal d-flex align-items-center h-100 btn btn-primary" title="Loading: {loading}">
          XXX
        </Button>
      </div>

      {error && (
        <div className="my-4 p-4 bg-red-800/20 ring-1 ring-red-500 rounded-lg text-red-300">
          <h3 className="font-bold">Error</h3>
          <pre className="whitespace-pre-wrap">{error.message}</pre>
        </div>
      )}

      <div className="relative -mx-4 mt-10 ring-1 ring-stash-700 sm:mx-0 sm:rounded-lg text-lg text-gray-50 bg-stash-600 shadow-lg shadow-stash-900">
        {loading && (
          <div className="absolute inset-0 bg-stash-800/50 flex items-center justify-center rounded-lg">
            <LoadingIndicator />
          </div>
        )}
      </div>
    </div>
  );
};
