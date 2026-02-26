import { Event, Uri } from 'vscode';

/**
 * Resource type for API methods
 */
export type Resource = Uri | undefined;

/**
 * Data provider interface for Data Viewer
 */
export interface IDataViewerDataProvider {
    // Data provider methods would be defined here
}

/**
 * Details for executing a Python interpreter
 */
export interface IExecutionCommandDetails {
    /**
     * Array of strings representing the command to execute.
     * E.g of execution commands returned could be,
     * * `['<path to the interpreter set in settings>']`
     * * `['<path to the interpreter selected by the extension when setting is not set>']`
     * * `['conda', 'run', 'python']` which is used to run from within Conda environments.
     * or something similar for some other Python environments.
     * 
     * Join the items using space to construct the full execution command.
     */
    command: string[];

    /**
     * Optional environment variables to set when executing the command.
     * If provided, these should be merged with the existing environment.
     * @example { PYTHONPATH: '/custom/path', CONDA_DEFAULT_ENV: 'myenv' }
     */
    env?: { [key: string]: string | undefined };

    /**
     * Optional working directory for execution.
     * If not provided, the workspace root or current directory should be used.
     */
    cwd?: string;
}

/**
 * Public API interface for the Python extension
 */
export interface IExtensionApi {
    /**
     * Promise indicating whether all parts of the extension have completed loading or not.
     * @type {Promise<void>}
     * @memberof IExtensionApi
     */
    ready: Promise<void>;

    debug: {
        /**
         * Generate an array of strings for commands to pass to the Python executable to launch the debugger for remote debugging.
         * Users can append another array of strings of what they want to execute along with relevant arguments to Python.
         * E.g `['/Users/..../pythonVSCode/pythonFiles/lib/python/debugpy', '--listen', 'localhost:57039', '--wait-for-client']`
         * @param {string} host
         * @param {number} port
         * @param {boolean} [waitUntilDebuggerAttaches=true]
         * @returns {Promise<string[]>}
         */
        getRemoteLauncherCommand(host: string, port: number, waitUntilDebuggerAttaches: boolean): Promise<string[]>;

        /**
         * Gets the path to the debugger package used by the extension.
         * @returns {Promise<string>}
         */
        getDebuggerPackagePath(): Promise<string | undefined>;
    };

    /**
     * Return internal settings within the extension which are stored in VSCode storage
     */
    settings: {
        /**
         * An event that is emitted when execution details (for a resource) change. For instance, when interpreter configuration changes.
         */
        readonly onDidChangeExecutionDetails: Event<Uri | undefined>;

        /**
         * Returns all the details the consumer needs to execute code within the selected environment,
         * corresponding to the specified resource taking into account any workspace-specific settings
         * for the workspace to which this resource belongs.
         * @param {Resource} [resource] A resource for which the setting is asked for.
         * * When no resource is provided, the setting scoped to the first workspace folder is returned.
         * * If no folder is present, it returns the global setting.
         * @returns {({ execCommand: IExecutionCommandDetails | undefined })}
         */
        getExecutionDetails(
            resource?: Resource
        ): {
            /**
             * Object containing the execution command and optionally environment variables.
             * When return value is `undefined`, it means no interpreter is set.
             */
            execCommand: IExecutionCommandDetails | undefined;
        };
    };

    datascience: {
        /**
         * Launches Data Viewer component.
         * @param {IDataViewerDataProvider} dataProvider Instance that will be used by the Data Viewer component to fetch data.
         * @param {string} title Data Viewer title
         */
        showDataViewer(dataProvider: IDataViewerDataProvider, title: string): Promise<void>;
    };
}
