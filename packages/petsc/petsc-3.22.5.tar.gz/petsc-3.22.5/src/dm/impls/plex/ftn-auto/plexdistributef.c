#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* plexdistribute.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscdmplex.h"
#include "petscdmlabel.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetadjacencyuseanchors_ DMPLEXSETADJACENCYUSEANCHORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetadjacencyuseanchors_ dmplexsetadjacencyuseanchors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetadjacencyuseanchors_ DMPLEXGETADJACENCYUSEANCHORS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetadjacencyuseanchors_ dmplexgetadjacencyuseanchors
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetadjacency_ DMPLEXGETADJACENCY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetadjacency_ dmplexgetadjacency
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatetwosidedprocesssf_ DMPLEXCREATETWOSIDEDPROCESSSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatetwosidedprocesssf_ dmplexcreatetwosidedprocesssf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributeownership_ DMPLEXDISTRIBUTEOWNERSHIP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributeownership_ dmplexdistributeownership
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreateoverlapmigrationsf_ DMPLEXCREATEOVERLAPMIGRATIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreateoverlapmigrationsf_ dmplexcreateoverlapmigrationsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexstratifymigrationsf_ DMPLEXSTRATIFYMIGRATIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexstratifymigrationsf_ dmplexstratifymigrationsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributefield_ DMPLEXDISTRIBUTEFIELD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributefield_ dmplexdistributefield
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributefieldis_ DMPLEXDISTRIBUTEFIELDIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributefieldis_ dmplexdistributefieldis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributedata_ DMPLEXDISTRIBUTEDATA
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributedata_ dmplexdistributedata
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetpartitionbalance_ DMPLEXSETPARTITIONBALANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetpartitionbalance_ dmplexsetpartitionbalance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetpartitionbalance_ DMPLEXGETPARTITIONBALANCE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetpartitionbalance_ dmplexgetpartitionbalance
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexcreatepointsf_ DMPLEXCREATEPOINTSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexcreatepointsf_ dmplexcreatepointsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexmigrate_ DMPLEXMIGRATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexmigrate_ dmplexmigrate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexremapmigrationsf_ DMPLEXREMAPMIGRATIONSF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexremapmigrationsf_ dmplexremapmigrationsf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistribute_ DMPLEXDISTRIBUTE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistribute_ dmplexdistribute
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributeoverlap_ DMPLEXDISTRIBUTEOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributeoverlap_ dmplexdistributeoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexgetoverlap_ DMPLEXGETOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexgetoverlap_ dmplexgetoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexsetoverlap_ DMPLEXSETOVERLAP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexsetoverlap_ dmplexsetoverlap
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributesetdefault_ DMPLEXDISTRIBUTESETDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributesetdefault_ dmplexdistributesetdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributegetdefault_ DMPLEXDISTRIBUTEGETDEFAULT
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributegetdefault_ dmplexdistributegetdefault
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexisdistributed_ DMPLEXISDISTRIBUTED
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexisdistributed_ dmplexisdistributed
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributionsetname_ DMPLEXDISTRIBUTIONSETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributionsetname_ dmplexdistributionsetname
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define dmplexdistributiongetname_ DMPLEXDISTRIBUTIONGETNAME
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define dmplexdistributiongetname_ dmplexdistributiongetname
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  dmplexsetadjacencyuseanchors_(DM dm,PetscBool *useAnchors, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetAdjacencyUseAnchors(
	(DM)PetscToPointer((dm) ),*useAnchors);
}
PETSC_EXTERN void  dmplexgetadjacencyuseanchors_(DM dm,PetscBool *useAnchors, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetAdjacencyUseAnchors(
	(DM)PetscToPointer((dm) ),useAnchors);
}
PETSC_EXTERN void  dmplexgetadjacency_(DM dm,PetscInt *p,PetscInt *adjSize,PetscInt *adj[], int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(adjSize);
*ierr = DMPlexGetAdjacency(
	(DM)PetscToPointer((dm) ),*p,adjSize,adj);
}
PETSC_EXTERN void  dmplexcreatetwosidedprocesssf_(DM dm,PetscSF sfPoint,PetscSection rootRankSection,IS rootRanks,PetscSection leafRankSection,IS leafRanks,IS *processRanks,PetscSF *sfProcess, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sfPoint);
CHKFORTRANNULLOBJECT(rootRankSection);
CHKFORTRANNULLOBJECT(rootRanks);
CHKFORTRANNULLOBJECT(leafRankSection);
CHKFORTRANNULLOBJECT(leafRanks);
PetscBool processRanks_null = !*(void**) processRanks ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(processRanks);
PetscBool sfProcess_null = !*(void**) sfProcess ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfProcess);
*ierr = DMPlexCreateTwoSidedProcessSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sfPoint) ),
	(PetscSection)PetscToPointer((rootRankSection) ),
	(IS)PetscToPointer((rootRanks) ),
	(PetscSection)PetscToPointer((leafRankSection) ),
	(IS)PetscToPointer((leafRanks) ),processRanks,sfProcess);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! processRanks_null && !*(void**) processRanks) * (void **) processRanks = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfProcess_null && !*(void**) sfProcess) * (void **) sfProcess = (void *)-2;
}
PETSC_EXTERN void  dmplexdistributeownership_(DM dm,PetscSection rootSection,IS *rootrank,PetscSection leafSection,IS *leafrank, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(rootSection);
PetscBool rootrank_null = !*(void**) rootrank ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(rootrank);
CHKFORTRANNULLOBJECT(leafSection);
PetscBool leafrank_null = !*(void**) leafrank ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(leafrank);
*ierr = DMPlexDistributeOwnership(
	(DM)PetscToPointer((dm) ),
	(PetscSection)PetscToPointer((rootSection) ),rootrank,
	(PetscSection)PetscToPointer((leafSection) ),leafrank);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! rootrank_null && !*(void**) rootrank) * (void **) rootrank = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! leafrank_null && !*(void**) leafrank) * (void **) leafrank = (void *)-2;
}
PETSC_EXTERN void  dmplexcreateoverlapmigrationsf_(DM dm,PetscSF overlapSF,PetscSF *migrationSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(overlapSF);
PetscBool migrationSF_null = !*(void**) migrationSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(migrationSF);
*ierr = DMPlexCreateOverlapMigrationSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((overlapSF) ),migrationSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! migrationSF_null && !*(void**) migrationSF) * (void **) migrationSF = (void *)-2;
}
PETSC_EXTERN void  dmplexstratifymigrationsf_(DM dm,PetscSF sf,PetscSF *migrationSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sf);
PetscBool migrationSF_null = !*(void**) migrationSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(migrationSF);
*ierr = DMPlexStratifyMigrationSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sf) ),migrationSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! migrationSF_null && !*(void**) migrationSF) * (void **) migrationSF = (void *)-2;
}
PETSC_EXTERN void  dmplexdistributefield_(DM dm,PetscSF pointSF,PetscSection originalSection,Vec originalVec,PetscSection newSection,Vec newVec, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pointSF);
CHKFORTRANNULLOBJECT(originalSection);
CHKFORTRANNULLOBJECT(originalVec);
CHKFORTRANNULLOBJECT(newSection);
CHKFORTRANNULLOBJECT(newVec);
*ierr = DMPlexDistributeField(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((pointSF) ),
	(PetscSection)PetscToPointer((originalSection) ),
	(Vec)PetscToPointer((originalVec) ),
	(PetscSection)PetscToPointer((newSection) ),
	(Vec)PetscToPointer((newVec) ));
}
PETSC_EXTERN void  dmplexdistributefieldis_(DM dm,PetscSF pointSF,PetscSection originalSection,IS originalIS,PetscSection newSection,IS *newIS, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pointSF);
CHKFORTRANNULLOBJECT(originalSection);
CHKFORTRANNULLOBJECT(originalIS);
CHKFORTRANNULLOBJECT(newSection);
PetscBool newIS_null = !*(void**) newIS ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newIS);
*ierr = DMPlexDistributeFieldIS(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((pointSF) ),
	(PetscSection)PetscToPointer((originalSection) ),
	(IS)PetscToPointer((originalIS) ),
	(PetscSection)PetscToPointer((newSection) ),newIS);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newIS_null && !*(void**) newIS) * (void **) newIS = (void *)-2;
}
PETSC_EXTERN void  dmplexdistributedata_(DM dm,PetscSF pointSF,PetscSection originalSection,MPI_Fint * datatype,void*originalData,PetscSection newSection,void**newData, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(pointSF);
CHKFORTRANNULLOBJECT(originalSection);
CHKFORTRANNULLOBJECT(newSection);
*ierr = DMPlexDistributeData(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((pointSF) ),
	(PetscSection)PetscToPointer((originalSection) ),
	MPI_Type_f2c(*(datatype)),originalData,
	(PetscSection)PetscToPointer((newSection) ),newData);
}
PETSC_EXTERN void  dmplexsetpartitionbalance_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexSetPartitionBalance(
	(DM)PetscToPointer((dm) ),*flg);
}
PETSC_EXTERN void  dmplexgetpartitionbalance_(DM dm,PetscBool *flg, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexGetPartitionBalance(
	(DM)PetscToPointer((dm) ),flg);
}
PETSC_EXTERN void  dmplexcreatepointsf_(DM dm,PetscSF migrationSF,PetscBool *ownership,PetscSF *pointSF, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(migrationSF);
PetscBool pointSF_null = !*(void**) pointSF ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(pointSF);
*ierr = DMPlexCreatePointSF(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((migrationSF) ),*ownership,pointSF);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! pointSF_null && !*(void**) pointSF) * (void **) pointSF = (void *)-2;
}
PETSC_EXTERN void  dmplexmigrate_(DM dm,PetscSF sf,DM targetDM, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(sf);
CHKFORTRANNULLOBJECT(targetDM);
*ierr = DMPlexMigrate(
	(DM)PetscToPointer((dm) ),
	(PetscSF)PetscToPointer((sf) ),
	(DM)PetscToPointer((targetDM) ));
}
PETSC_EXTERN void  dmplexremapmigrationsf_(PetscSF sfOverlap,PetscSF sfMigration,PetscSF *sfMigrationNew, int *ierr)
{
CHKFORTRANNULLOBJECT(sfOverlap);
CHKFORTRANNULLOBJECT(sfMigration);
PetscBool sfMigrationNew_null = !*(void**) sfMigrationNew ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sfMigrationNew);
*ierr = DMPlexRemapMigrationSF(
	(PetscSF)PetscToPointer((sfOverlap) ),
	(PetscSF)PetscToPointer((sfMigration) ),sfMigrationNew);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sfMigrationNew_null && !*(void**) sfMigrationNew) * (void **) sfMigrationNew = (void *)-2;
}
PETSC_EXTERN void  dmplexdistribute_(DM dm,PetscInt *overlap,PetscSF *sf,DM *dmParallel, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
PetscBool dmParallel_null = !*(void**) dmParallel ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmParallel);
*ierr = DMPlexDistribute(
	(DM)PetscToPointer((dm) ),*overlap,sf,dmParallel);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmParallel_null && !*(void**) dmParallel) * (void **) dmParallel = (void *)-2;
}
PETSC_EXTERN void  dmplexdistributeoverlap_(DM dm,PetscInt *overlap,PetscSF *sf,DM *dmOverlap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
PetscBool sf_null = !*(void**) sf ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(sf);
PetscBool dmOverlap_null = !*(void**) dmOverlap ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(dmOverlap);
*ierr = DMPlexDistributeOverlap(
	(DM)PetscToPointer((dm) ),*overlap,sf,dmOverlap);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! sf_null && !*(void**) sf) * (void **) sf = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! dmOverlap_null && !*(void**) dmOverlap) * (void **) dmOverlap = (void *)-2;
}
PETSC_EXTERN void  dmplexgetoverlap_(DM dm,PetscInt *overlap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLINTEGER(overlap);
*ierr = DMPlexGetOverlap(
	(DM)PetscToPointer((dm) ),overlap);
}
PETSC_EXTERN void  dmplexsetoverlap_(DM dm,DM dmSrc,PetscInt *overlap, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
CHKFORTRANNULLOBJECT(dmSrc);
*ierr = DMPlexSetOverlap(
	(DM)PetscToPointer((dm) ),
	(DM)PetscToPointer((dmSrc) ),*overlap);
}
PETSC_EXTERN void  dmplexdistributesetdefault_(DM dm,PetscBool *dist, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexDistributeSetDefault(
	(DM)PetscToPointer((dm) ),*dist);
}
PETSC_EXTERN void  dmplexdistributegetdefault_(DM dm,PetscBool *dist, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexDistributeGetDefault(
	(DM)PetscToPointer((dm) ),dist);
}
PETSC_EXTERN void  dmplexisdistributed_(DM dm,PetscBool *distributed, int *ierr)
{
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexIsDistributed(
	(DM)PetscToPointer((dm) ),distributed);
}
PETSC_EXTERN void  dmplexdistributionsetname_(DM dm, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = DMPlexDistributionSetName(
	(DM)PetscToPointer((dm) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  dmplexdistributiongetname_(DM dm, char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(dm);
*ierr = DMPlexDistributionGetName(
	(DM)PetscToPointer((dm) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
#if defined(__cplusplus)
}
#endif
