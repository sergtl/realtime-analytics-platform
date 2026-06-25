import { useMemo, useState } from "react";
import { toast } from "sonner";

import { ErrorAlert } from "@/components/error-alert";
import {
  useApiKeys,
  useCreateApiKey,
  useRevokeApiKey,
} from "@/hooks/use-api-keys";
import { Button } from "./ui/button";
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "./ui/field";
import { Input } from "./ui/input";
import { Skeleton } from "./ui/skeleton";

type ApiKeysProps = {
  projectId: string;
};

type RevokeCandidate = {
  id: string;
  name: string;
};

function formatDateTime(value: string | null) {
  if (!value) {
    return "Never used";
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

function ApiKeyListSkeleton() {
  return (
    <div className="grid gap-4">
      {Array.from({ length: 2 }).map((_, index) => (
        <Card key={index}>
          <CardHeader className="gap-2">
            <Skeleton className="h-4 w-32" />
            <Skeleton className="h-3 w-40" />
          </CardHeader>
          <CardContent className="space-y-2">
            <Skeleton className="h-3 w-44" />
            <Skeleton className="h-3 w-52" />
            <Skeleton className="h-8 w-32" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export function ApiKeys({ projectId }: ApiKeysProps) {
  const [apiKeyName, setApiKeyName] = useState("");
  const [createdRawKey, setCreatedRawKey] = useState<string | null>(null);
  const [createdApiKeyId, setCreatedApiKeyId] = useState<string | null>(null);
  const [revokeCandidate, setRevokeCandidate] =
    useState<RevokeCandidate | null>(null);
  const [revokingApiKeyId, setRevokingApiKeyId] = useState<string | null>(null);

  const { data = [], isPending, error } = useApiKeys(projectId);
  const {
    mutate: createApiKey,
    isPending: isCreatingApiKey,
    error: createApiKeyError,
  } = useCreateApiKey(projectId, {
    onSuccess: (result) => {
      setApiKeyName("");
      setCreatedRawKey(result.raw_key);
      setCreatedApiKeyId(result.api_key.id);
      toast.success(`Created ${result.api_key.name}.`);
    },
  });
  const {
    mutate: revokeApiKey,
    error: revokeApiKeyError,
  } = useRevokeApiKey(projectId, {
    onSuccess: (result) => {
      toast.success(`Revoked ${result.name}.`);
    },
  });

  const sortedApiKeys = useMemo(() => {
    return [...data].sort((left, right) => {
      const leftIsRevoked = left.revoked_at !== null;
      const rightIsRevoked = right.revoked_at !== null;

      if (leftIsRevoked !== rightIsRevoked) {
        return leftIsRevoked ? 1 : -1;
      }

      return (
        new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
      );
    });
  }, [data]);

  const activeApiKeys = useMemo(
    () => sortedApiKeys.filter((apiKey) => apiKey.revoked_at === null),
    [sortedApiKeys]
  );
  const revokedApiKeys = useMemo(
    () => sortedApiKeys.filter((apiKey) => apiKey.revoked_at !== null),
    [sortedApiKeys]
  );

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    createApiKey({
      name: apiKeyName.trim(),
    });
  }

  async function copyApiKey(apiKeyId: string, prefix: string) {
    if (createdRawKey && createdApiKeyId === apiKeyId) {
      await navigator.clipboard.writeText(createdRawKey);
      toast.success("API key copied.");
      return;
    }

    await navigator.clipboard.writeText(prefix);
    toast.message("Raw key unavailable", {
      description:
        "Only the key prefix is available now. Raw API keys are shown once when created.",
    });
  }

  function startRevokeFlow(apiKeyId: string, apiKeyName: string) {
    setRevokeCandidate({
      id: apiKeyId,
      name: apiKeyName,
    });
  }

  function cancelRevokeFlow() {
    if (revokingApiKeyId !== null) {
      return;
    }

    setRevokeCandidate(null);
  }

  function confirmRevokeApiKey() {
    if (!revokeCandidate) {
      return;
    }

    setRevokingApiKeyId(revokeCandidate.id);

    revokeApiKey(revokeCandidate.id, {
      onSettled: () => {
        setRevokingApiKeyId(null);
        setRevokeCandidate(null);
      },
    });
  }

  return (
    <section className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Create API key</CardTitle>
          <CardDescription>
            Use project-scoped API keys to send events into this workspace.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit}>
            <FieldGroup>
              {createApiKeyError ? (
                <ErrorAlert
                  title="Could not create API key"
                  description="Please try again. If the problem persists, check the API and try one more time."
                />
              ) : null}

              {revokeApiKeyError ? (
                <ErrorAlert
                  title="Could not revoke API key"
                  description="Please try again. If the problem persists, check the API and try one more time."
                />
              ) : null}

              {createdRawKey ? (
                <Card className="border-dashed">
                  <CardHeader>
                    <CardTitle className="text-base">
                      Copy this key now
                    </CardTitle>
                    <CardDescription>
                      Raw API keys are only shown once after creation.
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <code className="block overflow-x-auto border px-3 py-2 text-xs">
                      {createdRawKey}
                    </code>
                    <Button
                      type="button"
                      variant="outline"
                      className="cursor-pointer"
                      onClick={async () => {
                        await navigator.clipboard.writeText(createdRawKey);
                        toast.success("API key copied.");
                      }}
                    >
                      Copy key
                    </Button>
                  </CardContent>
                </Card>
              ) : null}

              <Field>
                <FieldLabel htmlFor="api-key-name">Key name</FieldLabel>
                <Input
                  id="api-key-name"
                  value={apiKeyName}
                  disabled={isCreatingApiKey}
                  placeholder="Production key"
                  onChange={(event) => setApiKeyName(event.target.value)}
                  required
                />
                <FieldDescription>
                  Give the key a name that makes its purpose obvious later.
                </FieldDescription>
              </Field>

              <Field>
                <div className="flex gap-3">
                  <Button
                    type="submit"
                    disabled={isCreatingApiKey || apiKeyName.trim() === ""}
                    className="cursor-pointer"
                  >
                    {isCreatingApiKey ? "Creating..." : "Create API key"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={isCreatingApiKey || apiKeyName === ""}
                    className="cursor-pointer"
                    onClick={() => setApiKeyName("")}
                  >
                    Clear
                  </Button>
                </div>
              </Field>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>

      <Dialog
        open={revokeCandidate !== null}
        onOpenChange={(open) => {
          if (!open) {
            cancelRevokeFlow();
          }
        }}
      >
        <DialogContent showCloseButton={revokingApiKeyId === null}>
          <DialogHeader>
            <DialogTitle>Revoke API key</DialogTitle>
            <DialogDescription>
              {revokeCandidate ? (
                <>
                  Revoke &quot;{revokeCandidate.name}&quot;? This key will stop
                  working immediately, but its record will remain visible for
                  reference.
                </>
              ) : null}
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              type="button"
              variant="destructive"
              disabled={revokingApiKeyId !== null}
              className="cursor-pointer"
              onClick={confirmRevokeApiKey}
            >
              {revokeCandidate && revokingApiKeyId === revokeCandidate.id
                ? "Revoking..."
                : "Confirm revoke"}
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={revokingApiKeyId !== null}
              className="cursor-pointer"
              onClick={cancelRevokeFlow}
            >
              Cancel
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {error ? (
        <ErrorAlert
          title="Could not load API keys"
          description="The dashboard could not fetch this project's API keys right now."
        />
      ) : null}

      {isPending ? <ApiKeyListSkeleton /> : null}

      {!isPending && activeApiKeys.length > 0 ? (
        <div className="flex flex-col gap-4">
          <div className="space-y-1">
            <h3 className="text-sm font-medium">Active keys</h3>
            <p className="text-sm text-muted-foreground">
              These keys can send events to this project right now.
            </p>
          </div>

          {activeApiKeys.map((apiKey) => (
            <Card key={apiKey.id}>
              <CardHeader>
                <div className="space-y-1">
                  <CardTitle>{apiKey.name}</CardTitle>
                  <CardDescription>{apiKey.prefix}</CardDescription>
                </div>
                <CardAction>
                  <Button
                    type="button"
                    variant="destructive"
                    disabled={revokingApiKeyId !== null}
                    className="cursor-pointer"
                    onClick={() => startRevokeFlow(apiKey.id, apiKey.name)}
                  >
                    {revokingApiKeyId === apiKey.id
                      ? "Revoking..."
                      : "Revoke key"}
                  </Button>
                </CardAction>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <p>Created: {formatDateTime(apiKey.created_at)}</p>
                <p>Last used: {formatDateTime(apiKey.last_used_at)}</p>
                <div className="flex gap-3 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="cursor-pointer"
                    onClick={() => copyApiKey(apiKey.id, apiKey.prefix)}
                  >
                    Copy key
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : null}

      {!isPending && revokedApiKeys.length > 0 ? (
        <div className="flex flex-col gap-4">
          <div className="space-y-1">
            <h3 className="text-sm font-medium">Revoked keys</h3>
            <p className="text-sm text-muted-foreground">
              These keys no longer work, but their history is kept for
              reference.
            </p>
          </div>

          {revokedApiKeys.map((apiKey) => (
            <Card key={apiKey.id} className="opacity-80">
              <CardHeader>
                <div className="space-y-1">
                  <CardTitle>{apiKey.name}</CardTitle>
                  <CardDescription>{apiKey.prefix}</CardDescription>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-sm text-muted-foreground">
                <p>Created: {formatDateTime(apiKey.created_at)}</p>
                <p>Last used: {formatDateTime(apiKey.last_used_at)}</p>
                <p>Revoked: {formatDateTime(apiKey.revoked_at)}</p>
                <div className="flex gap-3 pt-2">
                  <Button
                    type="button"
                    variant="outline"
                    className="cursor-pointer"
                    onClick={() => copyApiKey(apiKey.id, apiKey.prefix)}
                  >
                    Copy prefix
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : null}

      {!isPending && !error && data.length === 0 ? (
        <div className="flex flex-col items-start gap-2 p-2">
          <p className="pl-0.5">
            No API keys found. Create one to start tracking events.
          </p>
        </div>
      ) : null}
    </section>
  );
}
